# GenAI Learning — Coditas Technologies
> Internal training series | Maintained by Abhijeet Rajput (HyperX)

---

## Repo Structure

```
GENAI/genai/
├── README.md                        ← Start here
├── .env.example                     ← Copy to .env and add your key
├── .gitignore                       ← Protects your key from being pushed
│
├── genai-notes.md                   ← Session 1 & 2: concepts + prompt engineering
├── genai-applications.md            ← Session 2 hands-on: OpenRouter setup + app index
├── session3-own-model.md            ← Session 3: build your own AI tools (Steps 1–13)
│
├── applications/                    ← Runnable Python scripts (one per app)
│   ├── requirements.txt             ← pip install -r requirements.txt
│   ├── 01_basic_ask.py              ← Basic API call template
│   ├── 02_tictactoe.py              ← AI plays Tic-Tac-Toe (Session 2 demo)
│
└── genai-playground.jsx             ← Interactive React playground (Claude.ai)
```

---

## Sessions Overview

| # | Session | Topics | File |
|---|---------|--------|------|
| 1 | Foundations | 1.1 AI/ML/GenAI — 1.2 ChatGPT/Claude — 1.3 Tokens — 1.4 Context — 1.5 Temperature — 1.6 Roles | `genai-notes.md` |
| 2 | Prompt Engineering | 2.1 Zero-Shot — 2.2 Few-Shot — 2.3 Chain of Thought — 2.4 RBCFC — 2.5 Quick Reference | `genai-notes.md` |
| 3 | Build with Your Key | Steps 1–13: setup → parameters → apps → streaming → cost → fine-tuning → RAG | `session3-own-model.md` |

---

## Quick Start

```bash
# 1. Setup env
cp .env.example .env          # Mac/Linux
copy .env.example .env        # Windows
# Open .env and add your OpenRouter key

# 2. Create venv and install dependencies
python3 -m venv .venv
source .venv/bin/activate     # Mac/Linux
.venv\Scripts\activate        # Windows
pip install -r applications/requirements.txt

# 3. Run any app
.venv/bin/python applications/01_basic_ask.py
.venv/bin/python applications/02_tictactoe.py
```

---

## Approved Models (use only these)

| # | Model ID | Best For |
|---|----------|----------|
| 1 | `google/gemini-3.5-flash` | Fast tasks, writing, standup, basic Q&A |
| 2 | `minimax/minimax-m3` | Multi-turn conversations, chatbots |
| 3 | `qwen/qwen3.7-max` | Code generation, commit messages |
| 4 | `deepseek/deepseek-v4-pro` | Deep reasoning, log analysis, Terraform review |

> Do NOT use Anthropic or OpenAI models with the provided key.

---

## Key Concepts at a Glance

| # | Concept | One-liner |
|---|---------|-----------|
| 1 | Token | Unit of text an LLM reads (~0.75 words) |
| 2 | Context Window | Total tokens the model can see at once |
| 3 | Temperature | 0 = precise, 1.5 = creative/chaotic |
| 4 | System Prompt | Instructions that shape the model's behavior |
| 5 | Zero-Shot | Ask directly, no examples |
| 6 | Few-Shot | Show examples, then ask |
| 7 | Chain of Thought | Ask the model to reason step by step |
| 8 | RBCFC | Role, Background, Context, Format, Constraint |

---

## API Key Safety Rules

1. Never paste your key directly in any `.py` file
2. Always load from `.env` using `python-dotenv`
3. `.env` is in `.gitignore` — confirm before every `git push`
4. Never push to a public GitHub/GitLab repository
5. If the key is ever exposed, report to your session lead immediately

---

*Coditas Technologies GenAI Training | June 2026*
