"""
Application 02 — Tic-Tac-Toe AI
=================================
Demonstrates all three core prompting techniques applied to a game AI:
  - Technique 1: Zero-Shot   → ask the model for a move with no guidance
  - Technique 2: Few-Shot    → show example board → move pairs before asking
  - Technique 3: Chain of Thought (CoT) → ask the model to reason its move

The RBCFC framework is also visible here:
  Role       → "You are a Tic-Tac-Toe player playing as X"
  Context    → current board state passed every turn
  Format     → reply ONLY as row,col
  Constraint → only empty cells

Model: google/gemini-3.5-flash via OpenRouter

Setup:
  pip install openai python-dotenv
  copy .env.example .env   (then add your key)

Run:
  python 02_tictactoe.py
  Then choose which technique to use when prompted.
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


# ─────────────────────────────────────────────
# Board helpers
# ─────────────────────────────────────────────
def print_board(board):
    print()
    for i, row in enumerate(board):
        print(" | ".join(row))
        if i < 2:
            print("---------")
    print()


def board_to_str(board) -> str:
    return "\n".join([" | ".join(row) for row in board])


def check_winner(board):
    lines = (
        [board[i] for i in range(3)],
        [[board[r][i] for r in range(3)] for i in range(3)],
        [[board[i][i] for i in range(3)]],
        [[board[i][2-i] for i in range(3)]]
    )
    for group in lines:
        for line in group:
            if line[0] == line[1] == line[2] and line[0] != ".":
                return line[0]
    return None


def parse_move(text: str):
    """Extract row,col from model reply — handles CoT long responses too."""
    for part in text.replace("\n", " ").split():
        part = part.strip(".,;:()")
        if "," in part:
            try:
                r, c = map(int, part.split(","))
                if 0 <= r <= 2 and 0 <= c <= 2:
                    return r, c
            except ValueError:
                continue
    raise ValueError(f"Could not parse move from: {text}")


def safe_move(board, r, c):
    """If AI picks occupied cell, fallback to first empty cell."""
    if board[r][c] == ".":
        return r, c
    for fr in range(3):
        for fc in range(3):
            if board[fr][fc] == ".":
                return fr, fc
    return None, None


# ─────────────────────────────────────────────
# Technique 1 — Zero-Shot
# Just show the board and ask for a move. No examples. No reasoning.
# ─────────────────────────────────────────────
def get_move_zero_shot(board) -> tuple:
    system = (
        "You are a Tic-Tac-Toe player. You play as X. "
        "Rows and columns are 0, 1, 2. '.' means empty. "
        "Reply with ONLY your move as row,col (e.g. 1,2). Nothing else."
    )
    prompt = f"Board:\n{board_to_str(board)}\n\nYour move:"

    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": prompt}
    ]

    print("\n" + "═"*50)
    print("  📤 PROMPT SENT TO MODEL (Zero-Shot)")
    print("═"*50)
    print(f"  [SYSTEM]: {system}")
    print(f"  [USER]  : {prompt}")
    print("═"*50 + "\n")

    response = client.chat.completions.create(model=MODEL, messages=messages)
    reply = response.choices[0].message.content

    print(f"  📥 MODEL REPLY: {reply}\n")
    return parse_move(reply)


# ─────────────────────────────────────────────
# Technique 2 — Few-Shot
# Show two example board states and the correct moves before asking.
# Model learns the expected input/output format from examples.
# ─────────────────────────────────────────────
def get_move_few_shot(board) -> tuple:
    system = (
        "You are a Tic-Tac-Toe player. You play as X. "
        "Rows and columns are 0, 1, 2. '.' means empty. "
        "Reply with ONLY your move as row,col (e.g. 1,2). Nothing else."
    )

    print("\n" + "═"*50)
    print("  📤 PROMPT SENT TO MODEL (Few-Shot)")
    print("═"*50)
    print(f"  [SYSTEM]   : {system}")
    print("  [EXAMPLE 1 USER]: Board: X|X|. / .|O|. / .|.|O  →  Your move:")
    print("  [EXAMPLE 1 AI]  : 0,2  (take the win)")
    print("  [EXAMPLE 2 USER]: Board: O|O|. / X|.|. / X|.|.  →  Your move:")
    print("  [EXAMPLE 2 AI]  : 0,2  (block opponent)")
    print(f"  [REAL USER]: Board:\n{board_to_str(board)}\n  Your move:")
    print("═"*50 + "\n")

    messages = [
        {"role": "system", "content": system},
        {"role": "user",      "content": "Board:\nX | X | .\n. | O | .\n. | . | O\n\nYour move:"},
        {"role": "assistant", "content": "0,2"},
        {"role": "user",      "content": "Board:\nO | O | .\nX | . | .\nX | . | .\n\nYour move:"},
        {"role": "assistant", "content": "0,2"},
        {"role": "user",      "content": f"Board:\n{board_to_str(board)}\n\nYour move:"}
    ]
    response = client.chat.completions.create(model=MODEL, messages=messages)
    reply = response.choices[0].message.content

    print(f"  📥 MODEL REPLY: {reply}\n")
    return parse_move(reply)


# ─────────────────────────────────────────────
# Technique 3 — Chain of Thought (CoT)
# Ask the model to reason through the board before picking a move.
# It explains its thinking, then gives the final answer.
# ─────────────────────────────────────────────
def get_move_chain_of_thought(board) -> tuple:
    system = (
        "You are a Tic-Tac-Toe player. You play as X. "
        "Rows and columns are 0, 1, 2. '.' means empty. "
        "Think step by step: check for winning moves, then blocking moves, "
        "then strategic positions. "
        "End your response with your final move on its own line as row,col (e.g. 1,2)."
    )
    prompt = (
        f"Board:\n{board_to_str(board)}\n\n"
        "Think step by step and give your move:"
    )

    print("\n" + "═"*50)
    print("  📤 PROMPT SENT TO MODEL (Chain of Thought)")
    print("═"*50)
    print(f"  [SYSTEM]: {system}")
    print(f"  [USER]  : {prompt}")
    print("═"*50 + "\n")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt}
        ]
    )
    reply = response.choices[0].message.content

    print(f"  📥 MODEL REPLY (full reasoning):\n{reply}\n")
    return parse_move(reply)


# ─────────────────────────────────────────────
# Game loop
# ─────────────────────────────────────────────
TECHNIQUE_MAP = {
    "1": ("Zero-Shot",        get_move_zero_shot),
    "2": ("Few-Shot",         get_move_few_shot),
    "3": ("Chain of Thought", get_move_chain_of_thought),
}


def play(technique_key: str):
    name, get_move_fn = TECHNIQUE_MAP[technique_key]
    print(f"\nPlaying with Technique: {name}")
    print("You are O, AI is X. AI goes first.\n")

    board = [[".", ".", "."] for _ in range(3)]

    for turn in range(9):
        print_board(board)

        if turn % 2 == 0:
            print("AI is thinking...")
            while True:
                try:
                    r, c = get_move_fn(board)
                    r, c = safe_move(board, r, c)
                    if r is None:
                        print("Board full.")
                        break
                    board[r][c] = "X"
                    print(f"AI played: {r},{c}")
                    break
                except Exception as e:
                    print(f"AI error: {e}. Retrying...")
        else:
            while True:
                try:
                    move = input("Your move (row,col): ").strip()
                    r, c = map(int, move.split(","))
                    if board[r][c] != ".":
                        print("Cell taken. Try again.")
                        continue
                    board[r][c] = "O"
                    break
                except (ValueError, IndexError):
                    print("Invalid input. Use format row,col e.g. 1,2")

        winner = check_winner(board)
        if winner:
            print_board(board)
            print("AI wins!" if winner == "X" else "You win!")
            return

    print_board(board)
    print("Draw!")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Tic-Tac-Toe AI — Prompting Techniques Demo")
    print("=" * 50)
    print("\nChoose a prompting technique for the AI:")
    print("  1 — Zero-Shot        (no examples, direct ask)")
    print("  2 — Few-Shot         (examples shown first)")
    print("  3 — Chain of Thought (AI reasons step by step)")

    choice = input("\nEnter 1, 2, or 3: ").strip()
    if choice not in TECHNIQUE_MAP:
        print("Invalid choice. Defaulting to Zero-Shot.")
        choice = "1"

    play(choice)
