"""
LughaLLM Interactive Showcase Demo.
Runs an end-to-end demonstration of SWAHILI-BENCH, Dialect Detection, Agent Routing, and M-Pesa Billing.
"""

import sys
import os

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lughallm.src.orchestrator.agent import LughaOrchestrator
from lughallm.src.benchmark.swahili_bench import SwahiliBenchRunner
from lughallm.src.channels.ussd import ussd_manager
from lughallm.src.audio.voice import voice_processor
from lughallm.src.reasoning.thinker import reasoning_engine
from lughallm.src.agents.tools import tool_registry


def print_banner(title: str):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def run_demo():
    print_banner("LughaLLM — Foundational AI Infrastructure for East Africa")
    print("Addressing SDG 9 (Industry, Innovation & Infrastructure)")
    print("Target Audience: Developers, Enterprises, Governments")

    orchestrator = LughaOrchestrator()
    benchmark_runner = SwahiliBenchRunner()

    # 1. Benchmark Demo
    print_banner("1. SWAHILI-BENCH Evaluation Suite: Cultural & Dialect Benchmark")
    lugha_res = benchmark_runner.run_mock_simulation("lughallm")
    generic_res = benchmark_runner.run_mock_simulation("generic_base_llm")

    print(f"{'Metric':<30} | {'LughaLLM':<15} | {'Generic Base LLM':<15}")
    print("-" * 65)
    print(f"{'Overall Benchmark Score':<30} | {lugha_res['overall_score']*100:.1f}%{'':<10} | {generic_res['overall_score']*100:.1f}%")
    print(f"{'Pass Rate':<30} | {lugha_res['pass_rate']*100:.1f}%{'':<10} | {generic_res['pass_rate']*100:.1f}%")
    for cat, data in lugha_res["category_scores"].items():
        gen_score = generic_res["category_scores"].get(cat, {}).get("avg_score", 0.0)
        print(f"{cat.capitalize() + ' Accuracy':<30} | {data['avg_score']*100:.1f}%{'':<10} | {gen_score*100:.1f}%")

    # 2. Multi-Agent & Dialect Routing Demo
    print_banner("2. Pan-African Architecture: Multi-Dialect Detection Across 5 Nations")
    test_queries = [
        ("Kenya (Sheng)", "Manze jana mbogi yetu ilichanga ganji mob sana kujiandaa na shoo."),
        ("DRC Congo (Kingwana)", "Niko mu bureau ya Goma, nataka kuludia na sina l'argent ya moto leo."),
        ("Uganda (Trade Swahili)", "Tugende mu katale ya Kampala, ssebo anataka kulipa kodi ya URA kwa MoMo."),
        ("Tanzania (Kiswahili Sanifu)", "Mkulima wa mahindi Morogoro anapaswa kupalilia lini baada ya kupanda?"),
        ("EAC Regional Integration", "Je, Kiswahili kinatambuliwa rasmi kama lugha ya kufanyia kazi katika Umoja wa Afrika (AU) na SADC?")
    ]

    for idx, (country, q) in enumerate(test_queries, 1):
        result = orchestrator.route_and_execute(q)
        print(f"\n[Case {idx} — {country}] User Prompt: \"{q}\"")
        print(f"  -> Detected Dialect: {result['detected_dialect']}")
        print(f"  -> Routed Domain:    {result['routed_domain']} (Agent: {result['agent_name']})")
        print(f"  -> Agent Output:     {result['response']}")

    # 3. Mobile Money Billing Demo
    print_banner("3. Commercial Infrastructure: M-Pesa / Mobile Money Token Billing")
    amount_tzs = 10000.0
    rate = 25.0  # 25 TZS per 1k tokens
    tokens = int((amount_tzs / rate) * 1000)
    print(f"Customer deposits: TZS {amount_tzs:,.0f} via M-Pesa Daraja STK Push")
    print(f"Rate: TZS {rate} per 1,000 tokens")
    print(f"Tokens Credited to API Account: {tokens:,} tokens")
    print("Status: COMPLETED (Transaction reference: ws_CO_20261028_LUGHA)")

    # 4. Offline USSD Protocol Demo
    print_banner("4. Offline Feature-Phone Access: USSD Protocol (*149*00#)")
    ussd_menu = ussd_manager.process_ussd_request("sess_01", "*149*00#", "+255712345678", "")
    print("Step 1: User dials *149*00#:")
    print(ussd_menu)
    print("\nStep 2: User selects '1' (Kilimo):")
    ussd_sub = ussd_manager.process_ussd_request("sess_01", "*149*00#", "+255712345678", "1")
    print(ussd_sub)
    print("\nStep 3: User selects '1' (Mbolea ya Mahindi):")
    ussd_resp = ussd_manager.process_ussd_request("sess_01", "*149*00#", "+255712345678", "1*1")
    print(ussd_resp)

    # 5. Voice Note Audio Processing Demo
    print_banner("5. Multimodal Audio: WhatsApp Swahili Voice Note Transcription")
    voice_res = voice_processor.transcribe_audio_bytes("mkulima_morogoro.ogg", b"dummy_audio_bytes")
    print(f"Incoming Voice Note: {voice_res['filename']} ({voice_res['encoding']}, {voice_res['duration']}s)")
    print(f"Transcribed Text:    \"{voice_res['text']}\"")
    print(f"Detected Language:   {voice_res['language']} (Swahili)")

    # 6. AI-Native Deep Intelligence & Agentic Tools Demo
    print_banner("6. AI-Native Deep Intelligence: System-2 Thinking & Tool Execution")
    
    # 6a. Swahili Deep Reasoning Trace
    prompt_kodi = "Nina mapato ya KES 150,000 Kenya, nataka kujua VAT na jinsi ya kuwasilisha."
    print("6a. System-2 Explicit Reasoning Trace (<fikiri>...</fikiri>):")
    print(f"User Query: \"{prompt_kodi}\"")
    trace = reasoning_engine.generate_reasoning_trace(
        prompt=prompt_kodi,
        dialect="sheng_nairobi",
        domain="fedha_na_uchumi"
    )
    print(f"\nInternal Deliberation:\n{trace}\n")

    # 6b. Agentic Tool Execution
    print("6b. Autonomous Swahili Tool Calling:")
    print("Executing Tool: hesabu_kodi_kikanda (kiasi=150000, nchi=Kenya)")
    tax_res = tool_registry.execute_tool("hesabu_kodi_kikanda", {"kiasi": 150000, "nchi": "Kenya"})
    print(f"  -> VAT Rate:        {tax_res['kiwango_cha_vat']}")
    print(f"  -> Estimated VAT:    KES {tax_res['makisio_ya_vat']:,.2f}")
    print(f"  -> Total with VAT:   KES {tax_res['jumla_pamoja_na_vat']:,.2f}")

    print("\nExecuting Tool: pata_bei_za_soko (zao=mahindi, mji=Nairobi)")
    market_res = tool_registry.execute_tool("pata_bei_za_soko", {"zao": "mahindi", "mji": "Nairobi"})
    print(f"  -> Commodity Price:  {market_res['bei_ya_sasa']}")
    print(f"  -> Source:           {market_res['chanzo']}")

    print("\nExecuting Tool: rahisisha_mkopo_kidijitali (Mkopo=50,000, Rejesho=65,000, Siku=14)")
    loan_res = tool_registry.execute_tool("rahisisha_mkopo_kidijitali", {"kiasi_cha_mkopo": 50000, "kiasi_cha_kurejesha": 65000, "muda_siku": 14})
    print(f"  -> True Annual APR:  {loan_res['riba_ya_mwaka_apr']}")
    print(f"  -> Risk Assessment:  {loan_res['tathmini_ya_hatari']}")
    print(f"  -> Financial Advice: {loan_res['ushauri_wa_kifedha']}")

    print("\nExecuting Tool: tiba_ya_magonjwa_ya_mimea (Zao=mahindi, Shida=funza wa mahindi)")
    pest_res = tool_registry.execute_tool("tiba_ya_magonjwa_ya_mimea", {"zao": "mahindi", "dalili_au_mdudu": "funza wa mahindi"})
    print(f"  -> Diagnosis:        {pest_res['utambuzi']}")
    print(f"  -> Organic/Remedy:   {pest_res['tiba_na_kinga']}")

    print("\n6c. Cultural Etiquette & Adabu Engine:")
    adabu_input = "Shikamoo mwalimu, naomba msaada wa ushauri wa shamba langu."
    polite_output = reasoning_engine.apply_adabu_and_politeness(
        base_response="Niko tayari kukusaidia na miongozo ya kilimo bora.",
        prompt=adabu_input,
        dialect="kiswahili_sanifu"
    )
    print(f"User Input:     \"{adabu_input}\"")
    print(f"Polite Output:  \"{polite_output}\"")

    print("\n6d. Open-Weights Local Execution:")
    print("  -> Ollama Modelfile:  infra/Modelfile (Ollama run lughallm-8b)")
    print("  -> Edge Quantization: infra/export_gguf.py (Q4_K_M ~ 4.6GB RAM)")

    print_banner("Demo Completed Successfully!")


if __name__ == "__main__":
    run_demo()
