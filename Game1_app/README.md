# 🧩 8-Puzzle Solver Game

A desktop application for the classic **8-Puzzle Game**, built with **Python** and **Tkinter**.  
This app allows you to **play, scramble, and solve** the puzzle interactively, with features like an automatic solver using the **A\*** algorithm and a **leaderboard** to track your best performances!

---

## ✨ Features

- 🎮 Play the 8-puzzle interactively with a graphical interface  
- 🎲 Scramble the puzzle with selectable difficulty levels (Easy, Medium, Hard)  
- 🔀 Randomly generate solvable puzzle configurations  
- ↩️ Undo and Redo your moves  
- ⏱️ Timer and Move Counter to track performance  
- 🤖 Automatic Solver using the A\* algorithm with Manhattan distance heuristic  
- 🏆 Leaderboard to track top results based on moves, time, difficulty, and date  

---

## 🖥️ How to Run

### ✅ Requirements
- Python 3.7 or higher  
- The following Python packages:
  - `numpy`

### 📦 Install Dependencies
```bash
pip install numpy

---
🕹️ How to Play
Scramble: Scramble the puzzle from the solved state based on the selected difficulty.

Random: Generate a new random and solvable puzzle.

Solve: Automatically solve the current puzzle using the A* algorithm.

Undo/Redo: Step backward or forward through your move history.

Difficulty: Choose between Easy, Medium, or Hard levels of scramble depth.

Leaderboard: View the top 10 best performances tracked by moves and time.
