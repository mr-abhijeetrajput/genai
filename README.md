# GenAI Learning — Coditas Technologies
> Internal training series | Maintained by Abhijeet Rajput (HyperX)

---

## Repo Structure

```
GENAI/
├── README.md                  ← Start here
├── genai-notes.md             ← Session 1 & 2: concepts + prompt engineering
├── genai-applications.md      ← Session 2 hands-on: API key usage + DevOps apps
├── session3-own-model.md      ← Session 3: build your own AI tools step by step
├── genai-playground.jsx       ← Interactive React playground (run in Claude.ai)
└── Tictactoe-ai.py            ← Session 2 demo: Claude plays Tic-Tac-Toe via API
```

---

## Sessions Overview

| # | Session | Topics | File |
|---|---------|--------|------|
| 1 | Foundations | AI, ML, GenAI, LLMs, Tokens, Context, Temperature, Roles | `genai-notes.md` |
| 2 | Prompt Engineering | Zero-Shot, Few-Shot, Chain of Thought, RBCFC | `genai-notes.md` |
| 3 | Build with Your Key | API setup, parameters, apps, fine-tuning, RAG | `session3-own-model.md` |

---

## Quick Start

1. **Get your API key**
   - Anthropic (Claude): https://console.anthropic.com
   - OpenAI (GPT): https://platform.openai.com

2. **Set your key as an environment variable**
   ```bash
   # Windows — Command Prompt
   set ANTHROPIC_API_KEY=sk-ant-your-key-here

   # Windows — PowerShell
   $env:ANTHROPIC_API_KEY="sk-ant-your-key-here"

   # Mac / Linux
   export ANTHROPIC_API_KEY="sk-ant-your-key-here"
   ```

3. **Install the SDK and run the demo**
   ```bash
   pip install anthropic
   python Tictactoe-ai.py
   ```

4. **Try the interactive playground**
   - Open `genai-playground.jsx` → paste into Claude.ai as an artifact

---

## Key Concepts at a Glance

| Concept | One-liner |
|---------|-----------|
| Token | Unit of text an LLM reads (~0.75 words) |
| Context Window | Total tokens the model can see at once |
| Temperature | 0 = precise, 1.5 = creative/chaotic |
| System Prompt | Instructions that shape the model's behavior |
| Zero-Shot | Ask directly, no examples |
| Few-Shot | Show examples, then ask |
| Chain of Thought | Ask the model to reason step by step |
| RBCFC | Role, Background, Context, Format, Constraint |

---

## API Key Safety

1. Never push your key to GitHub
2. Always use environment variables or a `.env` file
3. Add `.env` to `.gitignore`
4. Set spend limits at console.anthropic.com

---

*Coditas Technologies GenAI Training | June 2026*
