"""
LughaLLM Model Export and Quantization Pipeline.

Features:
- Merges PEFT / LoRA adapter weights with the base foundation model (Meta-Llama-3-8B-Instruct).
- Generates llama.cpp GGUF conversion scripts and configuration for edge / CPU deployments.
- Generates production Ollama Modelfile with dialect-aware System-2 <fikiri> reasoning prompt.
- Gracefully handles CI / dry-run execution without PyTorch or Hugging Face installed.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LughaLLM.Export")

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    HAS_ML_EXPORT = True
except ImportError:
    HAS_ML_EXPORT = False
    logger.info("ML stack (torch/transformers/peft) not found. Running export in simulated/dry-run mode.")


DEFAULT_SYSTEM_PROMPT = """Wewe ni LughaLLM, muundo wa akili bandia wa kiwango cha juu (Deep Intelligence Foundation Model) ulioundwa mahsusi kwa ajili ya bara la Afrika, hasa wazungumzaji 150M+ wa Kiswahili katika nchi za Tanzania, Kenya, Jamhuri ya Kidemokrasia ya Kongo (DRC), Uganda, Rwanda, na Burundi.

MIONGOZO YAKO YA KIFIKRA NA MAJIBU:
1. FIKRA YA KINA (<fikiri>):
   Kwa maswali changamano (sheria, kodi za TRA/KRA/URA/DGI, utatuzi wa magonjwa ya kilimo, methali, misimu ya Sheng ya Nairobi, na Kingwana cha DRC), anza na sehemu ya <fikiri>...</fikiri> kuchambua:
   - Muktadha wa kiisimu (Kiswahili Sanifu, Nairobi Sheng, DRC Kingwana, au Uganda Trade).
   - Eneo husika la kijiografia na kikanuni.
   - Uthibitisho wa ukweli na kuzuia upotoshaji (hallucination defense).

2. KUEPUKA TAFSIRI YA NENO KWA NENO:
   Usiwahi kutafsiri nahau au methali kama neno kwa neno la Kiingereza. Eleza funzo, maadili, na maana halisi.

3. KULINDA USALAMA WA FEDHA NA KUZUIA UTAPELI WA SIMU (M-PESA / AIRTEL MONEY / MTN MOMO):
   Kamwe usishauri au kuhimiza mtumiaji kushiriki namba yake ya siri (PIN), namba za OTP, au kutuma fedha kwa madai ya kubonyeza linki za ajabu.

4. HESHIMA NA ADABU YA KITAMADUNI:
   Majibu yako yawe ya staha, fasaha, na yanayozingatia mshikamano wa kijamii na maendeleo ya kiuchumi ya Afrika Mashariki."""


def generate_ollama_modelfile(
    gguf_model_path_or_tag: str = "lughallm-8b-q4_k_m.gguf",
    output_path: Optional[str] = None,
    system_prompt: Optional[str] = None,
    temperature: float = 0.2,
    top_p: float = 0.9
) -> str:
    """
    Generates content for an Ollama Modelfile tailored for LughaLLM.
    """
    sys_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    modelfile_content = f"""# ==============================================================================
# LughaLLM - Production Ollama Modelfile
# Deep Intelligence & Multi-Dialect Swahili Foundation Model
# ==============================================================================

FROM {gguf_model_path_or_tag}

# Model Parameters
PARAMETER temperature {temperature}
PARAMETER top_p {top_p}
PARAMETER stop "<|eot_id|>"
PARAMETER stop "<|start_header_id|>"
PARAMETER stop "<|end_header_id|>"
PARAMETER stop "<|im_end|>"

# AI-Native System Prompt with System-2 <fikiri> Chain-of-Thought
SYSTEM \"\"\"{sys_prompt}\"\"\"
"""
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(modelfile_content)
        logger.info(f"Ollama Modelfile written to: {output_path}")

    return modelfile_content


def generate_gguf_conversion_script(
    merged_model_dir: str,
    output_dir: str,
    quant_types: Optional[List[str]] = None,
    context_length: int = 8192
) -> Dict[str, Any]:
    """
    Generates GGUF conversion instructions, metadata config, and helper shell script.
    """
    quants = quant_types or ["q4_k_m", "q8_0", "f16"]
    os.makedirs(output_dir, exist_ok=True)

    config_path = os.path.join(output_dir, "gguf_export_config.json")
    export_config = {
        "source_hf_dir": merged_model_dir,
        "output_gguf_dir": output_dir,
        "context_length": context_length,
        "target_quantizations": quants,
        "architecture": "llama",
        "llama_cpp_commands": {
            "convert_to_f16": f"python llama.cpp/convert_hf_to_gguf.py {merged_model_dir} --outtype f16 --outfile {os.path.join(output_dir, 'lughallm-8b-f16.gguf')}",
            "quantize": [
                f"./llama-quantize {os.path.join(output_dir, 'lughallm-8b-f16.gguf')} {os.path.join(output_dir, f'lughallm-8b-{q}.gguf')} {q.upper()}"
                for q in quants if q != "f16"
            ]
        }
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(export_config, f, indent=2)

    script_path = os.path.join(output_dir, "export_to_gguf.sh")
    script_lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        f"# LughaLLM GGUF Quantization Pipeline",
        f"MERGED_DIR=\"{merged_model_dir}\"",
        f"OUT_DIR=\"{output_dir}\"",
        "mkdir -p \"$OUT_DIR\"",
        "",
        "echo \"Step 1: Converting Hugging Face model to GGUF FP16...\"",
        f"python convert_hf_to_gguf.py \"$MERGED_DIR\" --outtype f16 --outfile \"$OUT_DIR/lughallm-8b-f16.gguf\"",
        ""
    ]
    for q in quants:
        if q != "f16":
            script_lines.append(f"echo \"Quantizing to {q.upper()}...\"")
            script_lines.append(f"./llama-quantize \"$OUT_DIR/lughallm-8b-f16.gguf\" \"$OUT_DIR/lughallm-8b-{q}.gguf\" {q.upper()}")

    with open(script_path, "w", encoding="utf-8") as f:
        f.write("\n".join(script_lines) + "\n")
    os.chmod(script_path, 0o755)

    return export_config


def merge_lora_weights(
    base_model_path: str = "meta-llama/Meta-Llama-3-8B-Instruct",
    adapter_path: str = "./lughallm-llama3-8b-lora",
    output_dir: str = "./lughallm-llama3-8b-merged",
    torch_dtype: str = "float16",
    device: str = "cpu",
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Merges LoRA adapter weights with the base model and saves unified weights.
    Supports dry_run simulation when PyTorch is not available.
    """
    logger.info("=" * 60)
    logger.info("  LughaLLM LoRA Weight Merging Pipeline")
    logger.info("=" * 60)
    logger.info(f"Base Model:    {base_model_path}")
    logger.info(f"LoRA Adapter:  {adapter_path}")
    logger.info(f"Output Merged: {output_dir}")

    os.makedirs(output_dir, exist_ok=True)
    is_dry_run = dry_run or not HAS_ML_EXPORT

    if is_dry_run:
        logger.info("Executing simulated / dry-run weight merge...")
        merged_config = {
            "_name_or_path": base_model_path,
            "architectures": ["LlamaForCausalLM"],
            "model_type": "llama",
            "vocab_size": 128256,
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "num_key_value_heads": 8,
            "num_hidden_layers": 32,
            "lughallm_merged_adapter": adapter_path,
            "torch_dtype": torch_dtype
        }
        with open(os.path.join(output_dir, "config.json"), "w", encoding="utf-8") as f:
            json.dump(merged_config, f, indent=2)

        # Write placeholder safetensors
        weights_file = os.path.join(output_dir, "model.safetensors")
        with open(weights_file, "wb") as f:
            f.write(b"LUGHALLM_MERGED_WEIGHTS_SAFE_TENSORS")

        merge_meta = {
            "status": "completed",
            "mode": "dry_run",
            "base_model": base_model_path,
            "adapter": adapter_path,
            "output_dir": output_dir,
            "config_path": os.path.join(output_dir, "config.json")
        }
        logger.info("Simulated LoRA merge completed successfully.")
        return merge_meta

    # Real Hardware Execution Path
    logger.info("Loading base model in floating point precision...")
    dtype = getattr(torch, torch_dtype, torch.float16)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        torch_dtype=dtype,
        device_map=device,
        trust_remote_code=True
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)

    logger.info(f"Attaching LoRA adapter from {adapter_path}...")
    model = PeftModel.from_pretrained(base_model, adapter_path)

    logger.info("Merging adapter into base model tensors...")
    merged_model = model.merge_and_unload()

    logger.info(f"Saving merged model to {output_dir}...")
    merged_model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    merge_meta = {
        "status": "completed",
        "mode": "real_gpu",
        "base_model": base_model_path,
        "adapter": adapter_path,
        "output_dir": output_dir
    }
    logger.info("LoRA weight merge completed successfully.")
    return merge_meta


def parse_args():
    parser = argparse.ArgumentParser(description="LughaLLM Model Export & GGUF / Ollama Pipeline")
    parser.add_argument("--base-model", type=str, default="meta-llama/Meta-Llama-3-8B-Instruct", help="Base model path")
    parser.add_argument("--adapter-dir", type=str, default="./lughallm-llama3-8b-lora", help="Trained LoRA adapter path")
    parser.add_argument("--output-dir", type=str, default="./lughallm-llama3-8b-merged", help="Output directory for merged model")
    parser.add_argument("--gguf-dir", type=str, default="./dist_gguf", help="Output directory for GGUF configs")
    parser.add_argument("--modelfile-path", type=str, default="./Modelfile", help="Path to generate Ollama Modelfile")
    parser.add_argument("--dry-run", action="store_true", help="Run simulated export without GPU")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    merge_lora_weights(
        base_model_path=args.base_model,
        adapter_path=args.adapter_dir,
        output_dir=args.output_dir,
        dry_run=args.dry_run
    )
    generate_gguf_conversion_script(
        merged_model_dir=args.output_dir,
        output_dir=args.gguf_dir
    )
    generate_ollama_modelfile(
        gguf_model_path_or_tag=os.path.join(args.gguf_dir, "lughallm-8b-q4_k_m.gguf"),
        output_path=args.modelfile_path
    )
