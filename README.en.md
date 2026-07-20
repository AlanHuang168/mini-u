# Mini-U · Quant Analysis Teaching Edition 🚀

[![CI](https://github.com/AlanHuang168/mini-u/actions/workflows/ci.yml/badge.svg)](https://github.com/AlanHuang168/mini-u/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

[简体中文](./README.md) | English

A **small but complete** teaching project for A-share quant analysis. With minimal code it
walks through an entire AI application pipeline: **collect real market data → rule-engine scoring →
DeepSeek deep analysis → render an HTML report** — plus "investment guru" role-play commentary and
multi-stock comparison, all driven by a single Streamlit UI.

> ⚠️ **Disclaimer**: This project is for technical teaching and demonstration only. None of its
> output constitutes investment advice.

## What you'll learn

The project deliberately isolates each of these concepts into its own module:

| Concept | Where it lives |
|---|---|
| **collect → analyze → render pipeline** | [`pipeline/`](pipeline/) |
| **Rule-engine + LLM hybrid decisions** (rules score, LLM explains) | [`rules/scoring.py`](rules/scoring.py) + [`pipeline/analyze.py`](pipeline/analyze.py) |
| **YAML role cards** (investment styles as config, not hard-coded) | [`roles/*.yaml`](roles/) |
| **Caching to cut token cost** (cache hit skips the LLM call) | [`pipeline/cache.py`](pipeline/cache.py) |
| **DeepSeek model calls** (OpenAI-compatible SDK) | [`pipeline/analyze.py`](pipeline/analyze.py) |
| **Streamlit presentation layer** | [`main.py`](main.py) |
| **Real data + graceful fallback** (Mock when akshare fails, never crashes) | [`pipeline/collect.py`](pipeline/collect.py) |

## Architecture

```text
                     User enters ticker(s) (Streamlit)
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                         ▼
   ┌─────────────┐         ┌───────────────┐         ┌───────────────┐
   │  collect     │         │  rule engine  │         │   analyze      │
   │ akshare real │  ──►    │ YAML scoring  │  ──►    │ DeepSeek+cache │
   │ fail→Mock    │         │ deterministic │         │ NL explanation │
   └─────────────┘         └───────────────┘         └───────┬───────┘
                                                             │
                                    ┌────────────────────────┤
                                    ▼                        ▼
                            ┌───────────────┐        ┌───────────────┐
                            │  render        │        │ role_play      │
                            │ self-contained │        │ YAML role card │
                            │ HTML report    │        │ commentary     │
                            └───────────────┘        └───────────────┘
```

**Design point**: the rule engine handles the "deterministic, explainable" scoring (price, change,
ROE and other hard metrics), while the LLM only "translates the score and data into plain language."
Clear separation of duties — that is the core idea of **rule + LLM hybrid decisions**.

## Quick start

Requires Python 3.10 or newer.

```bash
# 1. Clone
git clone https://github.com/AlanHuang168/mini-u.git
cd mini-u

# 2. Create and activate a virtual environment
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
streamlit run main.py
```

Then enter ticker(s) (e.g. `600519, 000333`, comma-separated) and click "🚀 Start".

## Configuring the DeepSeek API Key

LLM analysis and role commentary need a DeepSeek key ([get one here](https://platform.deepseek.com/)).
Pick any one of:

1. **In the UI** (recommended): paste it into the input box at the top of the Streamlit page. It
   stays in the current browser session only and is never written to disk.
2. **Environment variable**: copy `.env.example` to `.env` and set `DEEPSEEK_API_KEY=...`.
3. **No key**: check "demo mode" or leave the key blank to run on Mock data and canned text —
   the whole pipeline runs end-to-end at **zero cost**.

## Project layout

```text
mini-u/
├── main.py               # Streamlit entry (wires the whole pipeline)
├── SKILL.md              # Skill card (sub-command declarations)
├── requirements.txt      # Runtime dependencies
├── requirements-dev.txt  # Test dependencies
├── pipeline/             # ★ Core three-stage pipeline
│   ├── collect.py        #   collect: real akshare data + Mock fallback
│   ├── analyze.py        #   analyze: DeepSeek call + cache
│   ├── render.py         #   render: self-contained HTML report
│   └── cache.py          #   cache: keyed by ticker + TTL
├── rules/                # ★ Rule engine (deterministic scoring)
│   ├── scoring.py        #   rule evaluation logic
│   └── config/rules.yaml #   rule config (editable, no code change)
├── roles/                # ★ YAML role cards (Buffett / Cathie Wood / ...)
├── prompts/              # Prompt templates
├── skills/               # Sub-skills (role commentary, multi-stock compare)
├── tests/                # Unit tests (rule engine, offline)
└── docs/                 # Slides, deck, sample report
```

## Feature notes

### Real data + graceful fallback
[`collect.py`](pipeline/collect.py) fetches live quotes via [akshare](https://github.com/akfamily/akshare);
on any network failure or unknown code it **falls back to built-in Mock data** with a warning, so the
pipeline always runs and demos never break.

### Rule engine (configurable)
Scoring rules live in [`rules/config/rules.yaml`](rules/config/rules.yaml), e.g. "price > 1000 adds 15."
Changing rules needs **no Python edits** — just the YAML. Results include a recommendation and the list
of rules that fired, so scoring stays fully explainable.

### YAML role cards
Each "guru" is a [`roles/*.yaml`](roles/) defining `name / style / focus / prompt`. Adding a commentator
is just adding a YAML file — **personas driven by config**.

### Caching to cut cost
[`cache.py`](pipeline/cache.py) stores JSON keyed by `ticker + mode`, valid for 6 hours by default. A
cache hit returns immediately and **skips the DeepSeek call** — cheaper, and faster.

## Teaching stages

The project is split into 5 progressive stages (see [`docs/TECH_OVERVIEW.md`](docs/TECH_OVERVIEW.md)):

| Stage | Goal | Difficulty | Value |
|---|---|---|---|
| 1 | Understand the pipeline: split into collect → analyze → render | Low | Highest |
| 2 | Rules vs LLM: separate the rule engine from the LLM | Medium | High |
| 3 | Report generation: build a self-contained HTML report | Medium | High |
| 4 | Cache & robustness: add caching + fallback | Medium | Practical |
| 5 | Skill structure: add SKILL.md + multiple commands | Medium-high | Architecture |

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

Tests cover pure functions like the **rule engine** (offline, no LLM). CI runs them on every PR.

## Contributing

Issues and PRs welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md) first. Report security issues privately per [SECURITY.md](SECURITY.md).

## License

[MIT](./LICENSE) © 2026 AlanHuang168
