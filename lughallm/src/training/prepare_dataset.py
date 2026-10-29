"""
Dataset preparation and formatting pipeline for LughaLLM.
Converts raw East African text, proverbs, and Sheng dialogues into instruction-tuning format.
"""

import json
from typing import List, Dict, Any


def format_alpaca_sample(instruction: str, output: str, input_text: str = "") -> Dict[str, str]:
    return {
        "instruction": instruction,
        "input": input_text,
        "output": output
    }


def generate_seed_training_data() -> List[Dict[str, str]]:
    """Generates seed dataset for initial LoRA continued pretraining / SFT."""
    samples = [
        format_alpaca_sample(
            instruction="Eleza maana ya methali: 'Akiba haiozi'.",
            output="Methali 'Akiba haiozi' inamaanisha kuwa kitu chochote kinachowekwa akiba kwa ajili ya siku za baadaye hakipotei wala hakiharibiki bali kitamsaidia muhusika wakati wa shida."
        ),
        format_alpaca_sample(
            instruction="Nini tofauti ya Kiswahili Sanifu na Sheng ya Nairobi?",
            output="Kiswahili Sanifu ni lugha rasmi na sanifu inayofuata sarufi iliyoidhinishwa (inayozungumzwa shuleni, mahakamani na serikalini), ilhali Sheng ni lugha ya msimu (slang) ya vijana nchini Kenya inayochanganya Kiswahili, Kiingereza, na lugha za kiasili kama Kikuyu na Dholuo."
        ),
        format_alpaca_sample(
            instruction="Mteja amekwama kulipa bili ya LUKU kupitia simu. Mwelekeze hatua.",
            output="Mteja anapaswa: 1. Kupiga menyu ya mtandao wake (k.m. *150*00#), 2. Kuchagua 'Lipa Bili', 3. Kuchagua LUKU, 4. Kuingiza namba ya mita na kiasi, 5. Kuingiza nenosiri na kusubiri SMS yenye tarakimu za umeme (token)."
        ),
        format_alpaca_sample(
            instruction="Tafsiri kwa Sheng ya kisasa: 'Huyu mtu ana pesa nyingi sana'.",
            output="Kwa Sheng ya kisasa unaweza kusema: 'Huyu msee ako na ganji mob sana' au 'Huyu msee amepiga luku na anavuta chapaa kibao'."
        )
    ]
    return samples


def save_dataset_jsonl(samples: List[Dict[str, str]], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"Saved {len(samples)} instruction samples to {output_path}")


if __name__ == "__main__":
    import os
    out_dir = os.path.dirname(__file__)
    data = generate_seed_training_data()
    save_dataset_jsonl(data, os.path.join(out_dir, "swahili_instructions_seed.jsonl"))
