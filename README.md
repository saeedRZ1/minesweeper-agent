# Minesweeper Agent (CSP-like inference)

A Minesweeper game and AI agent implemented in pure Python.  
The AI uses logical sentences (sets of cells with mine counts) and subset inference to deduce safe moves and mines — similar in spirit to CS50's Minesweeper AI project.

## Features
- Game engine for Minesweeper (configurable board size and number of mines)
- Sentence-based knowledge representation and inference
- AI agent that marks safes/mines and picks moves (safe first, otherwise random)
- CLI interface for manual play and `auto` mode for AI play

## Files
- `minesweeper_agent.py` — main script (game + AI)

## How to run
```bash
# Let AI play on default 8x8 with 8 mines
python3 minesweeper_agent.py --play auto

# Play manually via simple CLI
python3 minesweeper_agent.py --play human --height 8 --width 8 --mines 8
```
## example 
AI revealed (6, 2) and hit a mine. Game over.
Result: won=False, moves=1, time=0.00s, flags=1
Final board (revealed states and flags):
<img width="155" height="177" alt="Screenshot 2025-09-24 211106" src="https://github.com/user-attachments/assets/d09de4d6-1684-4c30-8286-9f5e83069397" />


## Notes & Future improvements
- The AI uses basic logical inference and subset reasoning. Adding probabilistic reasoning and improved heuristics can raise success rates.
- A production-grade project would include unit tests, visualization (web or pygame), and more advanced inference rules.

## License
MIT
