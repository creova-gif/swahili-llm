"""
Unit tests for LughaLLM Training Pipeline, Dataset Preprocessing, QLoRA Configs, and Model Export.
"""

import os
import json
import shutil
import tempfile
import unittest

from lughallm.src.training.prepare_dataset import (
    format_alpaca_sample,
    format_chatml_sample,
    alpaca_to_chatml,
    chatml_to_alpaca,
    normalize_sample,
    verify_swahili_language,
    filter_sample,
    deduplicate_samples,
    split_dataset,
    prepare_training_splits,
    generate_seed_training_data,
    save_dataset_jsonl,
    load_dataset_jsonl,
    load_aya_dataset_subset,
    load_masakhane_subset
)
from lughallm.src.training.finetune_lora import (
    get_quantization_config,
    get_lora_config,
    get_training_args,
    format_instruction_text,
    run_training_pipeline,
    DEFAULT_TARGET_MODULES
)
from lughallm.src.training.export_model import (
    generate_ollama_modelfile,
    generate_gguf_conversion_script,
    merge_lora_weights
)


class TestSwahiliDatasetPreparation(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_format_alpaca_sample(self):
        sample = format_alpaca_sample(
            instruction="Eleza maana ya methali",
            output="Methali inamaanisha...",
            input_text="Akiba haiozi",
            metadata={"dialect": "sanifu"}
        )
        self.assertEqual(sample["instruction"], "Eleza maana ya methali")
        self.assertEqual(sample["input"], "Akiba haiozi")
        self.assertEqual(sample["output"], "Methali inamaanisha...")
        self.assertEqual(sample["metadata"]["dialect"], "sanifu")

    def test_format_chatml_sample(self):
        sample = format_chatml_sample(
            instruction="Habari yako?",
            output="Nzuri sana, nikusaidie vipi?",
            input_text="Muktadha wa salamu"
        )
        self.assertIn("messages", sample)
        messages = sample["messages"]
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn("Habari yako?", messages[1]["content"])
        self.assertIn("Muktadha wa salamu", messages[1]["content"])
        self.assertEqual(messages[2]["role"], "assistant")
        self.assertEqual(messages[2]["content"], "Nzuri sana, nikusaidie vipi?")

    def test_alpaca_chatml_bidirectional_conversion(self):
        alpaca = format_alpaca_sample(
            instruction="Tafsiri sentensi hii",
            output="Huu ni mfano wa tafsiri",
            input_text="Niaje morio"
        )
        chatml = alpaca_to_chatml(alpaca)
        self.assertIn("messages", chatml)

        converted_back = chatml_to_alpaca(chatml)
        self.assertEqual(converted_back["instruction"], alpaca["instruction"])
        self.assertEqual(converted_back["input"], alpaca["input"])
        self.assertEqual(converted_back["output"], alpaca["output"])

    def test_normalize_sample(self):
        raw_alpaca = {"instruction": "Jambo", "output": "Habari"}
        norm_alpaca = normalize_sample(raw_alpaca, target_format="alpaca")
        self.assertIn("instruction", norm_alpaca)
        self.assertIn("output", norm_alpaca)

        norm_chatml = normalize_sample(raw_alpaca, target_format="chatml")
        self.assertIn("messages", norm_chatml)

        # Reverse normalization
        back_to_alpaca = normalize_sample(norm_chatml, target_format="alpaca")
        self.assertEqual(back_to_alpaca["instruction"], "Jambo")
        self.assertEqual(back_to_alpaca["output"], "Habari")

    def test_verify_swahili_language(self):
        # Valid Swahili / Sheng / Kingwana texts
        self.assertTrue(verify_swahili_language("Habari ya asubuhi, nina shida na akaunti yangu ya simu"))
        self.assertTrue(verify_swahili_language("Mvumilivu hula mbivu, hiyo ni methali ya kale"))
        self.assertTrue(verify_swahili_language("Huyu msee ako na ganji mob sana mtaani"))
        self.assertTrue(verify_swahili_language("Jambo ndeko, tosha biloko hapa"))
        self.assertTrue(verify_swahili_language("Mkulima wa mahindi anahitaji mbolea ya kupandia DAP"))

        # Non-Swahili / Gibberish / Empty
        self.assertFalse(verify_swahili_language(""))
        self.assertFalse(verify_swahili_language("   "))
        self.assertFalse(verify_swahili_language("1234567 890 !@#$"))
        self.assertFalse(verify_swahili_language("The quick brown fox jumps over the lazy dog"))

    def test_filter_sample(self):
        valid_sample = format_alpaca_sample(
            instruction="Eleza kuhusu kilimo cha mahindi",
            output="Mahindi yanahitaji udongo wenye rutuba na mbolea ya DAP wakati wa kupanda."
        )
        self.assertTrue(filter_sample(valid_sample, verify_language=True))

        # Too short instruction/output
        short_sample = format_alpaca_sample(instruction="Hi", output="No")
        self.assertFalse(filter_sample(short_sample, min_chars=10))

        # Non-Swahili
        english_sample = format_alpaca_sample(
            instruction="Explain photosynthesis in plants",
            output="Photosynthesis is the process by which green plants transform light energy into chemical energy."
        )
        self.assertFalse(filter_sample(english_sample, verify_language=True))

    def test_deduplicate_samples(self):
        s1 = format_alpaca_sample("Swali moja", "Jibu moja")
        s2 = format_alpaca_sample("Swali moja", "Jibu lingine")  # Same instruction
        s3 = format_alpaca_sample("Swali la pili", "Jibu la pili")

        deduped = deduplicate_samples([s1, s2, s3])
        self.assertEqual(len(deduped), 2)
        self.assertEqual(deduped[0]["instruction"], "Swali moja")
        self.assertEqual(deduped[1]["instruction"], "Swali la pili")

    def test_split_dataset(self):
        samples = [format_alpaca_sample(f"Swali {i}", f"Jibu {i}") for i in range(100)]
        train_set, val_set = split_dataset(samples, val_ratio=0.15, seed=42)

        self.assertEqual(len(train_set), 85)
        self.assertEqual(len(val_set), 15)

        # Determinism check
        train_2, val_2 = split_dataset(samples, val_ratio=0.15, seed=42)
        self.assertEqual(train_set, train_2)
        self.assertEqual(val_set, val_2)

    def test_prepare_training_splits_pipeline(self):
        samples = generate_seed_training_data()[:20]
        stats = prepare_training_splits(
            samples=samples,
            output_dir=self.test_dir,
            val_ratio=0.2,
            output_format="alpaca",
            verify_language=True
        )

        self.assertTrue(os.path.exists(stats["train_path"]))
        self.assertTrue(os.path.exists(stats["val_path"]))
        self.assertGreater(stats["train_count"], 0)
        self.assertGreater(stats["val_count"], 0)
        self.assertEqual(stats["train_count"] + stats["val_count"], stats["deduped_count"])

        # Validate loaded splits
        loaded_train = load_dataset_jsonl(stats["train_path"])
        self.assertEqual(len(loaded_train), stats["train_count"])
        self.assertIn("instruction", loaded_train[0])

    def test_seed_dataset_integrity(self):
        seed_data = generate_seed_training_data()

        # Requirement: at least 50+ diverse pairs
        self.assertGreaterEqual(len(seed_data), 50, f"Expected >= 50 seed samples, got {len(seed_data)}")

        # Check coverage of required domains
        dialects = set()
        domains = set()
        for sample in seed_data:
            meta = sample.get("metadata", {})
            if "dialect" in meta:
                dialects.add(meta["dialect"])
            if "domain" in meta:
                domains.add(meta["domain"])

        expected_dialects = {
            "kiswahili_sanifu",
            "nairobi_sheng",
            "drc_kingwana",
            "uganda_trade",
            "mpesa_fraud_defense"
        }
        for d in expected_dialects:
            self.assertIn(d, dialects, f"Missing required dialect in seed dataset: {d}")

        # Check agriculture domain representation
        ag_samples = [s for s in seed_data if "kilimo" in str(s.get("metadata", {})) or "kilimo" in s.get("instruction", "").lower()]
        self.assertGreaterEqual(len(ag_samples), 5, "Seed dataset must contain agriculture (kilimo) samples")

        # Verify that all seed samples pass Swahili language verification
        for s in seed_data:
            self.assertTrue(
                filter_sample(s, verify_language=True),
                f"Seed sample failed language or length verification: {s['instruction']}"
            )

    def test_load_aya_and_masakhane_subset(self):
        # Test loading from sample file
        sample_path = os.path.join(self.test_dir, "sample_aya.jsonl")
        save_dataset_jsonl([
            {"inputs": "Eleza neno", "targets": "Neno ni kitengo cha lugha"}
        ], sample_path)

        aya_loaded = load_aya_dataset_subset(sample_path)
        self.assertEqual(len(aya_loaded), 1)
        self.assertEqual(aya_loaded[0]["instruction"], "Eleza neno")
        self.assertEqual(aya_loaded[0]["metadata"]["source"], "cohere_aya_swahili")

        masakhane_loaded = load_masakhane_subset(sample_path)
        # load_masakhane_subset checks for instruction/output or text/label
        self.assertEqual(len(masakhane_loaded), 0)  # inputs/targets belong to Aya


class TestLoRATrainingConfiguration(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_quantization_config(self):
        q_cfg = get_quantization_config(
            load_in_4bit=True,
            bnb_4bit_compute_dtype="bfloat16",
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
        if isinstance(q_cfg, dict):
            self.assertTrue(q_cfg["load_in_4bit"])
            self.assertEqual(q_cfg["bnb_4bit_quant_type"], "nf4")
            self.assertTrue(q_cfg["bnb_4bit_use_double_quant"])
        else:
            self.assertTrue(q_cfg.load_in_4bit)
            self.assertEqual(q_cfg.bnb_4bit_quant_type, "nf4")
            self.assertTrue(q_cfg.bnb_4bit_use_double_quant)

    def test_get_lora_config(self):
        lora_cfg = get_lora_config(
            r=16,
            lora_alpha=32,
            target_modules=DEFAULT_TARGET_MODULES,
            lora_dropout=0.05
        )
        if isinstance(lora_cfg, dict):
            self.assertEqual(lora_cfg["r"], 16)
            self.assertEqual(lora_cfg["lora_alpha"], 32)
            self.assertEqual(lora_cfg["lora_dropout"], 0.05)
            self.assertEqual(lora_cfg["target_modules"], DEFAULT_TARGET_MODULES)
        else:
            self.assertEqual(lora_cfg.r, 16)
            self.assertEqual(lora_cfg.lora_alpha, 32)
            self.assertEqual(lora_cfg.lora_dropout, 0.05)
            self.assertEqual(list(lora_cfg.target_modules), DEFAULT_TARGET_MODULES)

    def test_get_training_args(self):
        args = get_training_args(
            output_dir=self.test_dir,
            learning_rate=2e-4,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            gradient_checkpointing=True,
            lr_scheduler_type="cosine",
            warmup_steps=20
        )
        if isinstance(args, dict):
            self.assertEqual(args["learning_rate"], 2e-4)
            self.assertEqual(args["lr_scheduler_type"], "cosine")
            self.assertEqual(args["warmup_steps"], 20)
            self.assertEqual(args["gradient_accumulation_steps"], 4)
            self.assertTrue(args["gradient_checkpointing"])
        else:
            self.assertEqual(args.learning_rate, 2e-4)
            self.assertEqual(args.lr_scheduler_type, "cosine")
            self.assertEqual(args.warmup_steps, 20)
            self.assertEqual(args.gradient_accumulation_steps, 4)
            self.assertTrue(args.gradient_checkpointing)

    def test_format_instruction_text(self):
        alpaca = format_alpaca_sample("Maelekezo ya kulima", "Tumia mbolea", "Shamba la mahindi")
        text_alpaca = format_instruction_text(alpaca)
        self.assertIn("### Maelekezo:\nMaelekezo ya kulima", text_alpaca)
        self.assertIn("### Muktadha:\nShamba la mahindi", text_alpaca)
        self.assertIn("### Jibu:\nTumia mbolea", text_alpaca)

        chatml = alpaca_to_chatml(alpaca)
        text_chatml = format_instruction_text(chatml)
        self.assertIn("<|im_start|>user", text_chatml)
        self.assertIn("<|im_start|>assistant", text_chatml)
        self.assertIn("<|im_end|>", text_chatml)

    def test_run_training_pipeline_dry_run(self):
        summary = run_training_pipeline(
            base_model="meta-llama/Meta-Llama-3-8B-Instruct",
            data_path="swahili_instructions_seed.jsonl",
            output_dir=self.test_dir,
            epochs=2,
            learning_rate=2e-4,
            batch_size=2,
            lora_r=16,
            lora_alpha=32,
            dry_run=True
        )

        self.assertEqual(summary["status"], "completed")
        self.assertEqual(summary["lora_r"], 16)
        self.assertEqual(summary["lora_alpha"], 32)
        self.assertEqual(summary["learning_rate"], 2e-4)
        self.assertEqual(summary["target_modules"], DEFAULT_TARGET_MODULES)

        # Verify adapter_config.json was written to disk
        adapter_config_file = os.path.join(self.test_dir, "adapter_config.json")
        self.assertTrue(os.path.exists(adapter_config_file))
        with open(adapter_config_file, "r") as f:
            cfg = json.load(f)
            self.assertEqual(cfg["r"], 16)
            self.assertEqual(cfg["lora_alpha"], 32)
            self.assertEqual(cfg["target_modules"], DEFAULT_TARGET_MODULES)


class TestModelExportAndModelfile(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_generate_ollama_modelfile(self):
        modelfile_path = os.path.join(self.test_dir, "Modelfile")
        content = generate_ollama_modelfile(
            gguf_model_path_or_tag="lughallm-8b-q4_k_m.gguf",
            output_path=modelfile_path,
            temperature=0.2,
            top_p=0.9
        )

        self.assertTrue(os.path.exists(modelfile_path))
        self.assertIn("FROM lughallm-8b-q4_k_m.gguf", content)
        self.assertIn("PARAMETER temperature 0.2", content)
        self.assertIn("PARAMETER top_p 0.9", content)
        self.assertIn("<fikiri>", content)
        self.assertIn("M-PESA", content)

    def test_generate_gguf_conversion_script(self):
        gguf_dir = os.path.join(self.test_dir, "dist_gguf")
        export_config = generate_gguf_conversion_script(
            merged_model_dir="./test_merged",
            output_dir=gguf_dir,
            quant_types=["q4_k_m", "q8_0"]
        )

        config_path = os.path.join(gguf_dir, "gguf_export_config.json")
        script_path = os.path.join(gguf_dir, "export_to_gguf.sh")

        self.assertTrue(os.path.exists(config_path))
        self.assertTrue(os.path.exists(script_path))
        self.assertIn("q4_k_m", export_config["target_quantizations"])
        self.assertIn("q8_0", export_config["target_quantizations"])

        with open(script_path, "r") as f:
            script_text = f.read()
            self.assertIn("convert_hf_to_gguf.py", script_text)
            self.assertIn("llama-quantize", script_text)

    def test_merge_lora_weights_dry_run(self):
        merged_dir = os.path.join(self.test_dir, "merged")
        meta = merge_lora_weights(
            base_model_path="meta-llama/Meta-Llama-3-8B-Instruct",
            adapter_path="./test_adapter",
            output_dir=merged_dir,
            dry_run=True
        )

        self.assertEqual(meta["status"], "completed")
        config_path = os.path.join(merged_dir, "config.json")
        self.assertTrue(os.path.exists(config_path))
        with open(config_path, "r") as f:
            cfg = json.load(f)
            self.assertEqual(cfg["model_type"], "llama")
            self.assertEqual(cfg["lughallm_merged_adapter"], "./test_adapter")


if __name__ == "__main__":
    unittest.main()
