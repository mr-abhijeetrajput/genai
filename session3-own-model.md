# Session 3 — Using Your API Key & Building Your Own AI Tools
> From prompt engineering to actual products | Coditas GenAI Training

---

## What "Your Own Model" Really Means

You don't train a model from scratch (that costs millions of dollars and months of compute). What you *do* is:

1. **Use an existing model** (Claude, GPT-4, Llama) via API
2. **Control it completely** with your system prompt, temperature, and parameters
3. **Wrap it in your own app** — CLI tool, web app, bot, automation script
4. **Optionally fine-tune** it on your own data (advanced)

The API key is your access pass to the model. The system prompt is how you make it *yours*.

```
Your App  →  API Key  →  LLM Provider  →  Foundation Model
              (auth)     (Anthropic/OpenAI)  (Claude/GPT-4)
```

---

## Step 1 — Get Your API Key

### Anthropic (Claude)
1. Go to https://console.anthropic.com
2. Sign up / log in
3. Settings → API Keys → Create Key
4. Copy it immediately — shown only once

### OpenAI (GPT)
1. Go to https://platform.openai.com
2. Settings → API Keys → Create new secret key
3. Copy immediately

### Free alternatives (no credit card)
- **Google AI Studio** (Gemini): https://aistudio.google.com — generous free tier
- **Groq** (fast Llama): https://console.groq.com — free tier available
- **Ollama** (local, no key needed): https://ollama.ai — run models on your own machine

---

## Step 2 — Set Up Your Environment

```bash
# Install the SDK
pip install anthropic           # for Claude
pip install openai              # for GPT
pip install python-dotenv       # for .env file support

# Create a .env file in your project folder
echo ANTHROPIC_API_KEY=sk-ant-your-key-here > .env

# IMPORTANT: add to .gitignore
echo .env >> .gitignore
```

**Project structure:**
```
my-ai-tool/
├── .env              ← your keys (never commit)
├── .gitignore        ← includes .env
├── main.py           ← your app
└── requirements.txt  ← anthropic, python-dotenv
```

---

## Step 3 — Your First Real API Call

```python
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-sonnet-4-6",       # which model
    max_tokens=1024,                  # max output length
    temperature=0.3,                  # 0=precise, 1=creative
    system="You are a helpful DevOps engineer.",  # behavior
    messages=[
        {"role": "user", "content": "Explain what a Kubernetes namespace is."}
    ]
)

print(response.content[0].text)
```

**What the response object looks like:**
```python
response.content[0].text      # the actual reply text
response.usage.input_tokens   # tokens you sent
response.usage.output_tokens  # tokens in reply
response.model                # model that answered
response.stop_reason          # why it stopped (end_turn, max_tokens, etc.)
```

---

## Step 4 — Understanding Parameters

### `model`
Which AI to use. Affects capability, speed, and cost.

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| `claude-opus-4-6` | Slow | High | Complex reasoning, architecture |
| `claude-sonnet-4-6` | Medium | Medium | Most tasks — best balance |
| `claude-haiku-4-5-20251001` | Fast | Low | Quick lookups, high volume |

### `max_tokens`
Maximum tokens in the response. Set it appropriately:
- Simple answer: 200–500
- Code snippet: 500–1000
- Full document: 2000–4000

### `temperature`
```
0.0  → Deterministic. Same answer every time. Use for code, extraction.
0.3  → Slightly varied. Use for structured writing, summaries.
0.7  → Creative. Use for ideas, brainstorming, conversation.
1.0+ → Wild. Use for creative fiction, lateral thinking.
```

### `system`
The instruction layer. This is where your "model personality" lives.
Think of it as the permanent job description you give the model.

```python
# Bad system prompt (vague)
system = "Be helpful."

# Good system prompt (RBCFC)
system = """You are a senior Azure DevOps engineer at a fintech company.
You write concise, production-ready answers.
Always include CLI commands.
Never suggest solutions that require portal access.
Format code in code blocks."""
```

---

## Step 5 — Multi-Turn Conversations (Memory)

Models have no memory between API calls. You pass the full history each time.

```python
import anthropic, os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def chat(history, user_message, system="You are a helpful assistant."):
    history.append({"role": "user", "content": user_message})
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system,
        messages=history
    )
    
    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    return reply, history

# Usage
history = []
reply, history = chat(history, "Hi, I'm setting up AKS.")
print(reply)

reply, history = chat(history, "What node size should I use for general workloads?")
print(reply)
# Model remembers the AKS context from the previous message
```

---

## Step 6 — Structured Output (JSON from the model)

Make the model return JSON you can parse and use in code.

```python
import json

def get_structured_output(prompt: str) -> dict:
    system = """You are a data extractor.
Always respond with valid JSON only.
No markdown, no explanation, no backticks. Just the JSON object."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        temperature=0,      # deterministic for extraction tasks
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return json.loads(response.content[0].text)

# Example: extract info from a Kubernetes error
result = get_structured_output("""
Extract from this error: "0/3 nodes available: 3 Insufficient cpu."
Return JSON: {"error_type": "", "affected_resource": "", "root_cause": "", "fix": ""}
""")

print(result["fix"])
# → "Request fewer CPUs in your pod spec or scale up the cluster"
```

---

## Step 7 — Streaming Responses

For long outputs, stream tokens as they arrive (better UX):

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Write a detailed runbook for AKS upgrades."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

---

## Step 8 — Build a Real Tool: AI-Powered PR Description Generator

This is a complete, usable DevOps tool you can run today.

```python
"""
pr-description-generator.py
Usage: git diff main...HEAD | python pr-description-generator.py
"""

import anthropic, os, sys
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM = """You are a senior software engineer writing GitHub pull request descriptions.

Given a git diff, write a professional PR description with:
1. **What changed** — brief summary (2-3 sentences)
2. **Why** — business/technical reason
3. **Type** — feat / fix / refactor / chore / docs
4. **Testing** — what to test
5. **Checklist** — [ ] tests pass  [ ] docs updated  [ ] no secrets

Use markdown. Be concise and professional."""

def generate_pr_description(diff: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        temperature=0.3,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Git diff:\n\n{diff}"}]
    )
    return response.content[0].text

if __name__ == "__main__":
    diff = sys.stdin.read()
    if not diff.strip():
        print("No diff provided. Pipe a git diff into this script.")
    else:
        print(generate_pr_description(diff))
```

**Run it:**
```bash
git diff main...HEAD | python pr-description-generator.py
```

---

## Step 9 — Cost Estimation

Anthropic pricing (approximate, check console for current):

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|----------------------|
| Haiku 4.5 | ~$0.25 | ~$1.25 |
| Sonnet 4.6 | ~$3.00 | ~$15.00 |
| Opus 4.6 | ~$15.00 | ~$75.00 |

**Estimate your costs:**
```python
# Rough cost calculator
def estimate_cost(input_tokens, output_tokens, model="sonnet"):
    rates = {
        "haiku":  (0.25, 1.25),
        "sonnet": (3.00, 15.00),
        "opus":   (15.00, 75.00)
    }
    inp_rate, out_rate = rates[model]
    cost = (input_tokens / 1_000_000 * inp_rate) + (output_tokens / 1_000_000 * out_rate)
    return f"${cost:.6f}"

# Example: 500 input tokens, 300 output tokens with Sonnet
print(estimate_cost(500, 300, "sonnet"))  # ~$0.006
```

**Practical budget tips:**
- Use Haiku for high-volume, simple tasks (log parsing, classification)
- Use Sonnet for most real work (code review, analysis)
- Use Opus only for the most complex, high-stakes tasks

---

## What is Fine-Tuning? (Intro)

Fine-tuning = training an existing model further on your own data so it specializes.

| Approach | What you do | Cost | When to use |
|----------|------------|------|-------------|
| **Prompting** | Write a good system prompt | Free | 90% of cases |
| **Few-shot** | Add examples in the prompt | Free | When prompting isn't enough |
| **Fine-tuning** | Train on your dataset | $$$  | Specific domain, consistent style |
| **RAG** | Give model access to your docs | Low | Large knowledge base |

**For most company use cases, a well-crafted system prompt gets you 90% of the way there.** Fine-tuning is rarely needed at the start.

---

## RAG — Retrieval Augmented Generation (Intro)

RAG = give the model access to your documents at query time, rather than training it.

```
User asks question
       ↓
Search your document store (vector DB)
       ↓
Retrieve relevant chunks
       ↓
Inject into prompt: "Here are relevant docs: [chunks]. Now answer: [question]"
       ↓
Model answers using your docs as context
```

**Use case at Coditas:** RAG on internal runbooks, Confluence pages, incident reports.
Tools: LangChain, LlamaIndex, Pinecone, Azure AI Search.

---

## Recap: The Stack You Now Know

```
Layer 1 — Foundation Model    Claude / GPT-4 / Gemini / Llama
Layer 2 — API + Auth          API key, roles (system/user/assistant)
Layer 3 — Prompt Engineering  Zero-shot, Few-shot, CoT, RBCFC
Layer 4 — Your Application    Python scripts, web apps, CLI tools
Layer 5 — Parameters          Temperature, max_tokens, model choice
```

You now have everything you need to build real AI-powered tools.

---

## Next Steps

- [ ] Get your Anthropic API key from https://console.anthropic.com
- [ ] Run `Tictactoe-ai.py` with your key
- [ ] Build one of the applications from `genai-applications.md`
- [ ] Try the PR description generator above on a real diff
- [ ] Explore the React playground in `genai-playground.jsx`

---

*Session 3 notes maintained by: Abhijeet Rajput (HyperX) | Coditas Technologies | June 2026*
