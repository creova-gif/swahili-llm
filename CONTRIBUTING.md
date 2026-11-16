# Contributing to LughaLLM

Asante for helping! Bug fixes, new SWAHILI-BENCH cases and dialect data are all welcome.

## Setup

```bash
git clone https://github.com/creova-gif/swahili-llm.git
cd swahili-llm
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Before you open a pull request

1. Branch from `main` with a descriptive name, e.g. `feat/sheng-slang-cases`.
2. Run the tests: `python3 -m unittest discover -s lughallm/tests -p "test_*.py"`.
3. Run the benchmark: `python3 -m lughallm.src.benchmark.swahili_bench`.
4. Add tests for any behaviour you change.
5. Never commit API keys, `.env` files, model weights (`*.gguf`) or personal data.
6. Describe what changed, why, and how you tested it.

## Adding benchmark cases

Benchmark cases live in `lughallm/src/benchmark/dataset.json`. Include the dialect, the expected answer, and a source (native-speaker review, dictionary or published corpus) for each case.

## Reporting bugs and security issues

- Bugs and feature requests: open a GitHub issue with steps to reproduce.
- Security issues: email creativeinnovationspace@gmail.com instead of filing a public issue.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
