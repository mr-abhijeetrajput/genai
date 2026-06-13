"""
Application 03 — Simple Tic-Tac-Toe
=====================================
A stripped-down version of the Tic-Tac-Toe game.
No prompting technique selection — just you vs AI.
AI uses a basic Zero-Shot prompt to pick its move.

Model: google/gemini-3.5-flash via OpenRouter

Run:
  python 03_simple_tictactoe.py
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


def print_board(board):
    print()
    for i, row in enumerate(board):
        print(" | ".join(row))
        if i < 2:
            print("---------")
    print()


def check_winner(board):
    # rows, columns, diagonals
    lines = (
        [board[i]        for i in range(3)] +
        [[board[r][i]    for r in range(3)] for i in range(3)] +
        [[board[i][i]    for i in range(3)]] +
        [[board[i][2-i]  for i in range(3)]]
    )
    for line in lines:
        if line[0] == line[1] == line[2] and line[0] != ".":
            return line[0]
    return None


def ai_move(board):
    board_str = "\n".join([" | ".join(row) for row in board])
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Tic-Tac-Toe player. You play as X. "
                    "Rows and columns are 0, 1, 2. '.' means empty. "
                    "Reply with ONLY your move as row,col (e.g. 1,2). Nothing else."
                )
            },
            {
                "role": "user",
                "content": f"Board:\n{board_str}\n\nYour move:"
            }
        ]
    )
    reply = response.choices[0].message.content.strip()

    # parse row,col from reply
    for part in reply.replace("\n", " ").split():
        part = part.strip(".,;:()")
        if "," in part:
            try:
                r, c = map(int, part.split(","))
                if 0 <= r <= 2 and 0 <= c <= 2:
                    # fallback if cell is taken
                    if board[r][c] != ".":
                        for fr in range(3):
                            for fc in range(3):
                                if board[fr][fc] == ".":
                                    return fr, fc
                    return r, c
            except ValueError:
                continue
    # last resort fallback
    for fr in range(3):
        for fc in range(3):
            if board[fr][fc] == ".":
                return fr, fc


if __name__ == "__main__":
    print("=" * 40)
    print("  Simple Tic-Tac-Toe — You vs AI")
    print("  You are O, AI is X. AI goes first.")
    print("=" * 40)

    board = [[".", ".", "."] for _ in range(3)]

    for turn in range(9):
        print_board(board)

        if turn % 2 == 0:
            print("AI is thinking...")
            r, c = ai_move(board)
            board[r][c] = "X"
            print(f"AI played: {r},{c}")
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
                    print("Invalid. Use format: row,col  e.g. 1,2")

        winner = check_winner(board)
        if winner:
            print_board(board)
            print("AI wins!" if winner == "X" else "You win!")
            break
    else:
        print_board(board)
        print("Draw!")
