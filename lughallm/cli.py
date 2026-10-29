#!/usr/bin/env python3
"""
LughaLLM Developer CLI.
Interactive terminal client for testing, benchmarking, and managing API keys and M-Pesa balances.
"""

import sys
import os
import argparse
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lughallm.src.orchestrator.agent import LughaOrchestrator
from lughallm.src.benchmark.swahili_bench import SwahiliBenchRunner
from lughallm.src.db.storage import ledger
from lughallm.src.reasoning.thinker import reasoning_engine
from lughallm.src.agents.tools import tool_registry
import json


def cmd_chat(args):
    orchestrator = LughaOrchestrator()
    print("=" * 65)
    print("  LughaLLM Interactive Swahili Terminal (Kiswahili Sanifu & Sheng)")
    print("  Andika 'exit' au 'toka' kumaliza mazungumzo.")
    print("=" * 65)

    api_key = args.key or "lug_live_demo12345"
    key_info = ledger.get_key_info(api_key)
    if not key_info:
        print(f"Onyo: API key '{api_key}' haijapatikana. Inatumia demo key.")
        api_key = "lug_live_demo12345"

    while True:
        try:
            prompt = input("\nMtumiaji > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ["exit", "quit", "toka"]:
                print("Kwaheri! Asante kwa kutumia LughaLLM.")
                break

            start_t = time.time()
            res = orchestrator.route_and_execute(prompt, forced_dialect=args.dialect)
            duration = (time.time() - start_t) * 1000

            tokens_used = len(prompt.split()) * 2 + len(res["response"].split()) * 2
            cost_tzs = (tokens_used / 1000.0) * 25.0

            if getattr(args, "thinking", False):
                trace = reasoning_engine.generate_reasoning_trace(
                    prompt=prompt,
                    dialect=res["detected_dialect"],
                    domain=res["routed_domain"]
                )
                print(f"\n\033[90m{trace}\033[0m")

            # Debit from ledger
            ledger.debit_tokens(
                api_key=api_key,
                tokens=tokens_used,
                request_id=f"cli_{int(time.time())}",
                cost_tzs=cost_tzs,
                dialect=res["detected_dialect"],
                domain=res["routed_domain"]
            )

            print(f"\nLughaLLM [{res['agent_name']}] ({res['detected_dialect']}):")
            print(f"{res['response']}")
            print(f"\n[Stats: {tokens_used} tokens (~TZS {cost_tzs:.2f}) | Latency: {duration:.1f}ms]")

        except (KeyboardInterrupt, EOFError):
            print("\nKipindi kimefungwa.")
            break


def cmd_bench(args):
    print("=" * 65)
    print("  Inaendesha Tathmini Rasmi ya SWAHILI-BENCH")
    print("=" * 65)
    runner = SwahiliBenchRunner()
    results = runner.run_mock_simulation(model_profile=args.model)

    print(f"\nModel: {results['model_profile']}")
    print(f"Jumla ya Maswali: {results['total_items']}")
    print(f"Alama ya Jumla (Score): {results['overall_score']*100:.1f}%")
    print(f"Kiwango cha Kufaulu (Pass Rate): {results['pass_rate']*100:.1f}%")
    print("\nAlama kwa Kategoria:")
    for cat, info in results["category_scores"].items():
        print(f"  - {cat:<25}: {info['avg_score']*100:.1f}% (Mifano: {info['count']})")


def cmd_key(args):
    if args.action == "create":
        key = ledger.create_api_key(name=args.name, initial_tokens=args.tokens)
        info = ledger.get_key_info(key)
        print("\nAPI Key Mpya Imetengenezwa:")
        print(f"  Jina:    {info['name']}")
        print(f"  API Key: {info['api_key']}")
        print(f"  Token:   {info['balance_tokens']:,}")
        print("\nWeka ufunguo huu mahali salama: export LUGHALLM_API_KEY=" + info['api_key'])
    elif args.action == "balance":
        info = ledger.get_key_info(args.key)
        if not info:
            print(f"Hitilafu: API Key '{args.key}' haipo.")
            sys.exit(1)
        print(f"\nTaarifa za Akaunti ({info['name']}):")
        print(f"  API Key:       {info['api_key']}")
        print(f"  Salio la Token: {info['balance_tokens']:,}")
        print(f"  Hali (Status): {'Inafanya kazi' if info['is_active'] else 'Imesitishwa'}")


def cmd_tools(args):
    if args.action == "list":
        print("=" * 65)
        print("  LughaLLM Sajili ya Vyombo vya Kujitegemea (Agentic Tools)")
        print("=" * 65)
        tools = tool_registry.get_tool_definitions()
        for idx, t in enumerate(tools, 1):
            fn = t["function"]
            print(f"\n{idx}. Chombo: {fn['name']}")
            print(f"   Maelezo: {fn['description']}")
            print(f"   Vigezo:  {json.dumps(fn['parameters'], ensure_ascii=False)}")
    elif args.action == "run":
        args_dict = json.loads(args.args) if args.args else {}
        print(f"Inatekeleza: {args.name}...")
        res = tool_registry.execute_tool(args.name, args_dict)
        print("\nMatokeo ya Chombo:")
        print(json.dumps(res, indent=2, ensure_ascii=False))


def cmd_topup(args):
    print("=" * 65)
    print("  M-Pesa Daraja STK Push — Token Top-up")
    print("=" * 65)
    tokens_to_credit = int((args.amount / 25.0) * 1000)
    checkout_id = f"ws_CO_{int(time.time())}"

    new_bal = ledger.credit_tokens(
        api_key=args.key,
        tokens=tokens_to_credit,
        checkout_id=checkout_id,
        phone=args.phone,
        amount_tzs=args.amount
    )

    print(f"Namba ya Simu: {args.phone}")
    print(f"Kiasi:         TZS {args.amount:,.0f}")
    print(f"Token Zilizoongezwa: {tokens_to_credit:,}")
    print(f"Salio Jipya:   {new_bal:,} tokens")
    print(f"Hali:          COMPLETED (Tx: {checkout_id})")


def main():
    parser = argparse.ArgumentParser(description="LughaLLM Swahili AI CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # chat
    p_chat = subparsers.add_parser("chat", help="Start interactive terminal chat")
    p_chat.add_argument("--key", type=str, default="lug_live_demo12345", help="API Key")
    p_chat.add_argument("--dialect", type=str, default="auto", choices=["auto", "kiswahili_sanifu", "sheng_nairobi"])
    p_chat.add_argument("--thinking", action="store_true", help="Print Swahili <fikiri> System-2 reasoning traces")
    p_chat.set_defaults(func=cmd_chat)

    # bench
    p_bench = subparsers.add_parser("bench", help="Run SWAHILI-BENCH evaluation")
    p_bench.add_argument("--model", type=str, default="lughallm", choices=["lughallm", "generic_base_llm"])
    p_bench.set_defaults(func=cmd_bench)

    # tools
    p_tools = subparsers.add_parser("tools", help="Agentic tools & function calling")
    p_tools_sub = p_tools.add_subparsers(dest="action", required=True)
    p_t_list = p_tools_sub.add_parser("list", help="List registered Swahili tools")
    p_t_run = p_tools_sub.add_parser("run", help="Run a registered tool")
    p_t_run.add_argument("--name", type=str, required=True, help="Tool name")
    p_t_run.add_argument("--args", type=str, default="{}", help="JSON string arguments")
    p_tools.set_defaults(func=cmd_tools)

    # key
    p_key = subparsers.add_parser("key", help="Manage API keys")
    p_key_sub = p_key.add_subparsers(dest="action", required=True)
    p_k_create = p_key_sub.add_parser("create", help="Create new key")
    p_k_create.add_argument("--name", type=str, required=True, help="Application name")
    p_k_create.add_argument("--tokens", type=int, default=50000, help="Initial tokens")
    p_k_bal = p_key_sub.add_parser("balance", help="Check key balance")
    p_k_bal.add_argument("--key", type=str, required=True, help="API Key")
    p_key.set_defaults(func=cmd_key)

    # topup
    p_topup = subparsers.add_parser("topup", help="Simulate M-Pesa token purchase")
    p_topup.add_argument("--phone", type=str, default="255712345678", help="Phone number")
    p_topup.add_argument("--amount", type=float, default=5000.0, help="TZS amount")
    p_topup.add_argument("--key", type=str, default="lug_live_demo12345", help="Target API key")
    p_topup.set_defaults(func=cmd_topup)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
