"""
Tic-Tac-Toe AI — GenAI Session 2 Demo
Uses Claude API with a constrained system prompt (RBCFC example)

Install: pip install anthropic
Usage:   python tictactoe_ai.py
"""

import anthropic
import os

# ─── Config ────────────────────────────────────────────────────
API_KEY = os.getenv("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
MODEL   = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """You are a Tic-Tac-Toe player. You play as X.
Rows and columns are 0, 1, 2 (top-left is 0,0).
Only choose empty cells.
Reply with ONLY the move in format row,col (e.g. 1,2). No other text."""

# ─── Board Helpers ─────────────────────────────────────────────

def empty_board():
    return [[None, None, None] for _ in range(3)]

def print_board(board):
    symbols = {None: " ", "X": "X", "O": "O"}
    print()
    for i, row in enumerate(board):
        print(f"  {symbols[row[0]]} | {symbols[row[1]]} | {symbols[row[2]]}")
        if i < 2:
            print("  ---------")
    print()

def check_winner(board):
    lines = [
        [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],  # rows
        [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],  # cols
        [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)],                        # diagonals
    ]
    for line in lines:
        vals = [board[r][c] for r, c in line]
        if vals[0] and all(v == vals[0] for v in vals):
            return vals[0]
    if all(board[r][c] for r in range(3) for c in range(3)):
        return "Draw"
    return None

def board_to_prompt(board):
    symbols = {None: " ", "X": "X", "O": "O"}
    rows = "\n".join([
        f"| {symbols[board[r][0]]} | {symbols[board[r][1]]} | {symbols[board[r][2]]} |"
        for r in range(3)
    ])
    return f"""Current board (empty= , X, O). Board rows:
{rows}
You are X. What is your move? Reply row,col only."""

# ─── AI Move ───────────────────────────────────────────────────

def get_ai_move(board):
    client = anthropic.Anthropic(api_key=API_KEY)
    
    response = client.messages.create(
        model=MODEL,
        max_tokens=10,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": board_to_prompt(board)}]
    )
    
    move = response.content[0].text.strip()
    row, col = map(int, move.split(","))
    return row, col

# ─── Game Loop ─────────────────────────────────────────────────

def play_game():
    board = empty_board()
    print("\n🎮 Tic-Tac-Toe: You (O) vs Claude AI (X)")
    print("Board positions: row,col where 0,0 = top-left\n")
    
    # Decide who goes first
    first = input("Who goes first? (you/ai): ").strip().lower()
    current = "ai" if first == "ai" else "human"
    
    while True:
        print_board(board)
        
        if current == "human":
            while True:
                try:
                    move = input("Your move (row,col): ").strip()
                    r, c = map(int, move.split(","))
                    if board[r][c] is None:
                        board[r][c] = "O"
                        break
                    else:
                        print("Cell already taken. Try again.")
                except (ValueError, IndexError):
                    print("Invalid input. Use format: row,col (e.g. 1,2)")
        else:
            print("Claude is thinking...")
            try:
                r, c = get_ai_move(board)
                if board[r][c] is None:
                    board[r][c] = "X"
                    print(f"Claude plays: {r},{c}")
                else:
                    print("Claude chose an occupied cell — picking first empty...")
                    for ri in range(3):
                        for ci in range(3):
                            if board[ri][ci] is None:
                                board[ri][ci] = "X"
                                print(f"Claude plays: {ri},{ci}")
                                break
                        else:
                            continue
                        break
            except Exception as e:
                print(f"AI error: {e}")
                break
        
        winner = check_winner(board)
        if winner:
            print_board(board)
            if winner == "Draw":
                print("🤝 It's a draw!")
            elif winner == "X":
                print("🤖 Claude (X) wins!")
            else:
                print("🎉 You (O) win!")
            break
        
        current = "ai" if current == "human" else "human"

# ─── Entry ─────────────────────────────────────────────────────

if __name__ == "__main__":
    play_game()