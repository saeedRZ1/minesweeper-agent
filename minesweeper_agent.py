#!/usr/bin/env python3
"""
minesweeper_agent.py

A self-contained Minesweeper game + AI agent implementation inspired by CS50 AI project.
- No external dependencies (pure Python 3).
- Run `python3 minesweeper_agent.py --play auto` to let the AI play a full game.
- Run `python3 minesweeper_agent.py --play human` to play manually in the terminal.

Author: Saeed Razmara
License: MIT
"""
import random
import argparse
import time
from copy import deepcopy
from typing import List, Set, Tuple

Position = Tuple[int, int]


class Minesweeper:
    def __init__(self, height: int = 8, width: int = 8, mines: int = 8):
        self.height = height
        self.width = width
        self.mines_count = mines

        self.board = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.mines: Set[Position] = set()
        while len(self.mines) < mines:
            r = random.randrange(self.height)
            c = random.randrange(self.width)
            if (r, c) not in self.mines:
                self.mines.add((r, c))
                self.board[r][c] = True

        self.revealed: Set[Position] = set()
        self.flags: Set[Position] = set()

    def in_bounds(self, pos: Position) -> bool:
        r, c = pos
        return 0 <= r < self.height and 0 <= c < self.width

    def neighbors(self, pos: Position) -> Set[Position]:
        (r, c) = pos
        neighbors = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    neighbors.add((nr, nc))
        return neighbors

    def nearby_mines(self, pos: Position) -> int:
        return sum(1 for n in self.neighbors(pos) if n in self.mines)

    def is_mine(self, pos: Position) -> bool:
        return pos in self.mines

    def reveal(self, pos: Position) -> int:
        if pos in self.revealed:
            return self.nearby_mines(pos)
        self.revealed.add(pos)
        if pos in self.mines:
            return -1
        return self.nearby_mines(pos)

    def won(self) -> bool:
        total_cells = self.height * self.width
        return len(self.revealed) == total_cells - len(self.mines)

    def print_board(self, reveal_mines: bool = False):
        for r in range(self.height):
            row_str = []
            for c in range(self.width):
                pos = (r, c)
                if pos in self.revealed:
                    if pos in self.mines:
                        cell = "X"
                    else:
                        cell = str(self.nearby_mines(pos))
                elif pos in self.flags:
                    cell = "F"
                else:
                    cell = "."
                if reveal_mines and pos in self.mines:
                    cell = "M" if cell == "." else cell
                row_str.append(cell.rjust(2))
            print("".join(row_str))
        print()


class Sentence:
    def __init__(self, cells: Set[Position], count: int):
        self.cells: Set[Position] = set(cells)
        self.count: int = count

    def __repr__(self):
        return f"Sentence({self.cells}, {self.count})"

    def known_mines(self) -> Set[Position]:
        if len(self.cells) == 0:
            return set()
        if self.count == len(self.cells):
            return set(self.cells)
        return set()

    def known_safes(self) -> Set[Position]:
        if self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, pos: Position):
        if pos in self.cells:
            self.cells.remove(pos)
            self.count -= 1

    def mark_safe(self, pos: Position):
        if pos in self.cells:
            self.cells.remove(pos)

    def is_empty(self) -> bool:
        return len(self.cells) == 0


class MinesweeperAI:
    def __init__(self, height: int = 8, width: int = 8):
        self.height = height
        self.width = width
        self.moves_made: Set[Position] = set()
        self.safes: Set[Position] = set()
        self.mines: Set[Position] = set()
        self.knowledge: List[Sentence] = []

    def mark_mine(self, pos: Position):
        self.mines.add(pos)
        for s in self.knowledge:
            s.mark_mine(pos)

    def mark_safe(self, pos: Position):
        self.safes.add(pos)
        for s in self.knowledge:
            s.mark_safe(pos)

    def add_knowledge(self, cell: Position, count: int, game: Minesweeper):
        self.moves_made.add(cell)
        self.mark_safe(cell)

        neighbors = game.neighbors(cell)
        unknowns = set(n for n in neighbors if n not in self.safes and n not in self.mines and n not in self.moves_made)
        known_mines_in_neighbors = sum(1 for n in neighbors if n in self.mines)
        new_count = count - known_mines_in_neighbors
        new_sentence = Sentence(unknowns, new_count)
        if not new_sentence.is_empty():
            self.knowledge.append(new_sentence)

        changed = True
        while changed:
            changed = False
            safes = set()
            mines = set()
            for s in self.knowledge:
                safes |= s.known_safes()
                mines |= s.known_mines()

            for s_pos in safes:
                if s_pos not in self.safes:
                    self.mark_safe(s_pos)
                    changed = True
            for m_pos in mines:
                if m_pos not in self.mines:
                    self.mark_mine(m_pos)
                    changed = True

            self.knowledge = [s for s in self.knowledge if not s.is_empty()]

            new_inferred = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 == s2:
                        continue
                    if s1.cells and s2.cells and s1.cells.issubset(s2.cells):
                        diff_cells = s2.cells - s1.cells
                        diff_count = s2.count - s1.count
                        inferred = Sentence(diff_cells, diff_count)
                        if not inferred.is_empty() and inferred not in self.knowledge and inferred not in new_inferred:
                            new_inferred.append(inferred)
            if new_inferred:
                self.knowledge.extend(new_inferred)
                changed = True

    def make_safe_move(self):
        for s in self.safes:
            if s not in self.moves_made:
                return s
        return None

    def make_random_move(self):
        choices = []
        for r in range(self.height):
            for c in range(self.width):
                pos = (r, c)
                if pos in self.moves_made or pos in self.mines:
                    continue
                choices.append(pos)
        if not choices:
            return None
        return random.choice(choices)


def run_ai_game(height=8, width=8, mines=8, verbose=True):
    game = Minesweeper(height, width, mines)
    ai = MinesweeperAI(height, width)
    start_time = time.time()
    moves = 0

    while True:
        move = ai.make_safe_move()
        if move is None:
            move = ai.make_random_move()
            if move is None:
                break

        result = game.reveal(move)
        moves += 1
        if result == -1:
            if verbose:
                print(f"AI revealed {move} and hit a mine. Game over.")
            ai.mark_mine(move)
            break
        else:
            ai.add_knowledge(move, result, game)

        if game.won():
            if verbose:
                print("AI won the game!")
            break

    elapsed = time.time() - start_time
    return {
        "won": game.won(),
        "moves": moves,
        "elapsed": elapsed,
        "explored_flags": len(ai.mines),
        "game": game,
        "ai": ai
    }


def human_play_cli(height=8, width=8, mines=8):
    game = Minesweeper(height, width, mines)
    print("Welcome to Minesweeper (CLI).")
    while True:
        game.print_board()
        cmd = input("Enter command (reveal r c / flag r c / quit): ").strip().lower()
        if cmd == "quit":
            break
        parts = cmd.split()
        if len(parts) < 3:
            print("Invalid command.")
            continue
        action = parts[0]
        try:
            r = int(parts[1]); c = int(parts[2])
        except ValueError:
            print("Invalid coordinates.")
            continue
        pos = (r, c)
        if action == "reveal":
            res = game.reveal(pos)
            if res == -1:
                print("Boom! You hit a mine. Game over.")
                game.print_board(reveal_mines=True)
                break
            else:
                print(f"Nearby mines: {res}")
                if game.won():
                    print("You won! Congratulations.")
                    game.print_board(reveal_mines=True)
                    break
        elif action == "flag":
            game.flags.add(pos)
        else:
            print("Unknown action.")


def main():
    parser = argparse.ArgumentParser(description="Minesweeper AI project - agent + game")
    parser.add_argument("--play", choices=["human", "auto"], default="auto", help="Run mode: human or auto (AI)")
    parser.add_argument("--height", type=int, default=8)
    parser.add_argument("--width", type=int, default=8)
    parser.add_argument("--mines", type=int, default=8)
    args = parser.parse_args()

    if args.play == "human":
        human_play_cli(args.height, args.width, args.mines)
    else:
        result = run_ai_game(args.height, args.width, args.mines, verbose=True)
        print(f"Result: won={result['won']}, moves={result['moves']}, time={result['elapsed']:.2f}s, flags={result['explored_flags']}")
        print("Final board (revealed states and flags):")
        result['game'].print_board(reveal_mines=True)


if __name__ == "__main__":
    main()
