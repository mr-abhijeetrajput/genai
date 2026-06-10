"""
Application 01 — Basic Ask
============================
A simple demonstration of how to send a question to an LLM and get a response.

Model: google/gemini-3.5-flash via OpenRouter

Setup:
  pip install openai python-dotenv
  copy .env.example .env   (then add your key)

Run:
  python 01_basic_ask.py
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "google/gemini-3.5-flash"


def ask(question: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": question}
        ]
    )
    return {
        "answer": response.choices[0].message.content.strip(),
        "prompt_tokens":     response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens":      response.usage.total_tokens
    }


if __name__ == "__main__":
    print("=" * 60)
    print("  Basic Ask — type 'exit' to quit")
    print("=" * 60)

    while True:
        question = input("\nAsk anything: ").strip()

        if question.lower() in ("exit", "quit", "q"):
            print("Bye!")
            break

        if not question:
            continue

        print("\nThinking...\n")
        result = ask(question)

        print("-" * 60)
        print(f"A: {result['answer']}")
        print("-" * 60)
        print(f"Tokens used  →  prompt: {result['prompt_tokens']}  |  response: {result['completion_tokens']}  |  total: {result['total_tokens']}")
