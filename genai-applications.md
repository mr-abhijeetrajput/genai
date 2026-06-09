# GenAI Applications & API Key Usage
> Hands-on uses for your API key — DevOps, automation, and personal projects

---

## Your API Key — What It Unlocks

Once you have an API key (OpenAI or Anthropic), you can call the model directly:

```bash
# Test your Anthropic key with curl
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_KEY_HERE" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-6",
    "max_tokens": 500,
    "messages": [
      {"role": "user", "content": "Explain AKS node pools in 3 bullet points."}
    ]
  }'
```

```bash
# Test your OpenAI key with curl
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role": "user", "content": "Explain AKS node pools in 3 bullet points."}
    ]
  }'
```

---

## Application 1 — Python Script to Call Claude

```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def ask_claude(question, system_prompt=None):
    messages = [{"role": "user", "content": question}]
    
    kwargs = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1024,
        "messages": messages
    }
    if system_prompt:
        kwargs["system"] = system_prompt
    
    response = client.messages.create(**kwargs)
    return response.content[0].text

# Basic usage
answer = ask_claude("What is Kubernetes?")
print(answer)

# With RBCFC system prompt
system = "You are a Senior DevOps Engineer. Answer concisely with CLI commands where relevant."
answer = ask_claude("How do I check why a pod is in Pending state?", system)
print(answer)
```

Install: `pip install anthropic`

---

## Application 2 — Tic-Tac-Toe AI with Your Key

> This is the demo from Session 2 — using a structured system prompt to make the model play a game.

The system prompt used:
```
You are a Tic-Tac-Toe player. You play as X.
Rows and columns are 0, 1, 2 (top-left is 0,0).
Only choose empty cells.
Reply with ONLY the move in format row,col (e.g. 1,2). No other text.
```

This is **RBCFC in action:**
- **Role:** Tic-Tac-Toe player
- **Constraint:** Only empty cells, reply format is row,col only

See `Tictactoe-ai.py` for the full implementation.

**The key lesson here:** The system prompt constrains the model to behave like a specialized function — not a general chatbot. This is the foundation of building AI-powered tools.

---

## Application 3 — DevOps: Kubernetes Log Analyzer

Paste a kubectl log dump, get an instant root cause analysis.

```python
import anthropic, os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def analyze_k8s_logs(logs: str) -> str:
    system = """You are a Senior Kubernetes SRE.
Analyze the provided pod logs.
Output format:
1. Root Cause (1 sentence)
2. Severity: Critical / High / Medium / Low
3. Fix Steps (numbered, with kubectl commands)
4. Prevention (1 sentence)"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=system,
        messages=[{"role": "user", "content": f"Analyze these logs:\n\n{logs}"}]
    )
    return response.content[0].text

# Usage
with open("pod-logs.txt") as f:
    logs = f.read()

analysis = analyze_k8s_logs(logs)
print(analysis)
```

---

## Application 4 — Terraform Code Reviewer

```python
def review_terraform(tf_code: str) -> str:
    system = """You are a Terraform expert and Azure DevOps engineer.
Review the provided Terraform code.
Check for:
- Security issues (exposed secrets, public endpoints, missing encryption)
- Azure best practices violations
- Missing tags or naming convention issues
- Cost optimization opportunities
Format as a table: Issue | Severity | Recommendation"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=system,
        messages=[{"role": "user", "content": f"Review this Terraform:\n\n```hcl\n{tf_code}\n```"}]
    )
    return response.content[0].text
```

---

## Application 5 — Commit Message Generator

```python
def generate_commit_message(git_diff: str) -> str:
    system = """You are a developer writing git commit messages.
Follow Conventional Commits format: type(scope): description
Types: feat, fix, chore, docs, refactor, test
Reply with ONLY the commit message. No explanation."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        system=system,
        messages=[{"role": "user", "content": f"Write a commit message for:\n{git_diff}"}]
    )
    return response.content[0].text
```

---

## Application 6 — Daily Standup Generator

```python
def generate_standup(yesterday: str, today: str, blockers: str = "None") -> str:
    system = """You are a professional DevOps engineer writing a standup update.
Keep it concise, clear, and under 100 words. No fluff."""

    prompt = f"""
Yesterday: {yesterday}
Today: {today}
Blockers: {blockers}
Write my standup update."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

---

## Application 7 — Interactive Terminal Chatbot

```python
import anthropic, os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
conversation_history = []
SYSTEM = "You are a Senior DevOps Engineer. Be concise. Use CLI commands when relevant."

print("DevOps AI Assistant (type 'exit' to quit)\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "exit":
        break
    
    conversation_history.append({"role": "user", "content": user_input})
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SYSTEM,
        messages=conversation_history
    )
    
    assistant_reply = response.content[0].text
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    print(f"\nAssistant: {assistant_reply}\n")
```

---

## API Key Safety Rules

- **Never hardcode your key** in code you push to GitHub
- Store in environment variable: `export ANTHROPIC_API_KEY="sk-ant-..."`
- Or use a `.env` file + `python-dotenv` library
- Set usage limits/alerts on the API dashboard
- Rotate keys if accidentally exposed

```python
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

`.env` file (never commit this):
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

`.gitignore` entry:
```
.env
```

---

## Quick Reference — Which Model to Use

| Task | Model | Why |
|------|-------|-----|
| Complex reasoning, architecture | claude-opus-4-6 | Most capable |
| General DevOps, code review | claude-sonnet-4-6 | Best balance |
| Quick lookups, simple tasks | claude-haiku-4-5-20251001 | Fastest, cheapest |
| GPT alternative | gpt-4o | OpenAI equivalent |

---

*Applications reference maintained by: Abhijeet Rajput (HyperX) | Coditas Technologies | June 2026*
