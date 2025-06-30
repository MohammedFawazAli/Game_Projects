import numpy as np
import random
import tkinter as tk
import time
from threading import Thread
import os
import datetime

# --- 8-Puzzle Logic ---
class EightPuzzleEnv:
    def __init__(self):
        self.size = 3
        self.goal = tuple(range(1, self.size*self.size)) + (0,)
        self.state = self.goal

    def reset(self):
        while True:
            perm = list(range(self.size*self.size))
            random.shuffle(perm)
            if self._is_solvable(perm):
                break
        self.state = tuple(perm)
        return self.state

    def _is_solvable(self, perm):
        inv = 0
        arr = [p for p in perm if p != 0]
        for i in range(len(arr)):
            for j in range(i+1, len(arr)):
                if arr[i] > arr[j]: inv += 1
        return inv % 2 == 0

def manhattan_distance(state, goal):
    size = int(len(state) ** 0.5)
    dist = 0
    for i, tile in enumerate(state):
        if tile == 0:
            continue
        goal_idx = goal.index(tile)
        x1, y1 = divmod(i, size)
        x2, y2 = divmod(goal_idx, size)
        dist += abs(x1 - x2) + abs(y1 - y2)
    return dist

def get_neighbors(state, size):
    neighbors = []
    zero_idx = state.index(0)
    x, y = divmod(zero_idx, size)
    moves = [(-1,0), (1,0), (0,-1), (0,1)]
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < size and 0 <= ny < size:
            nidx = nx * size + ny
            new_state = list(state)
            new_state[zero_idx], new_state[nidx] = new_state[nidx], new_state[zero_idx]
            neighbors.append(tuple(new_state))
    return neighbors

def a_star(start, goal):
    import heapq
    size = int(len(start) ** 0.5)
    heap = []
    heapq.heappush(heap, (manhattan_distance(start, goal), 0, start, []))
    cost_so_far = {start: 0}
    while heap:
        est_total, cost, state, path = heapq.heappop(heap)
        if state == goal:
            return path + [state]
        for neighbor in get_neighbors(state, size):
            new_cost = cost + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heapq.heappush(heap, (
                    new_cost + manhattan_distance(neighbor, goal),
                    new_cost,
                    neighbor,
                    path + [state]
                ))
    return None

class EightPuzzleGUI:
    LEADERBOARD_FILE = 'leaderboard.txt'
    LEADERBOARD_SIZE = 10

    def __init__(self, master):
        self.master = master
        master.title("8-Puzzle Solver")
        self.env = EightPuzzleEnv()
        self.state = self.env.goal
        self.buttons = []
        self.move_count = 0
        self.solving = False
        self.start_time = None
        self.elapsed_time = 0
        self.timer_running = False
        self.timer_id = None
        self.history = []  # For undo
        self.future = []   # For redo
        self.difficulty = tk.StringVar(value="Medium")
        self.create_widgets()
        self.update_grid()

    def create_widgets(self):
        self.frame = tk.Frame(self.master, bg="#222")
        self.frame.pack(pady=10)
        self.tile_size = 100  # Fixed size for square tiles
        for i in range(3):
            row = []
            for j in range(3):
                btn = tk.Button(self.frame, text='', width=1, height=1, font=('Arial', 32, 'bold'),
                                relief='raised', bd=4, bg="#f0e68c", fg="#222",
                                activebackground="#ffe4b5",
                                command=lambda x=i, y=j: self.move_tile(x, y))
                btn.grid(row=i, column=j, padx=2, pady=2, sticky="nsew")
                btn.config(width=self.tile_size//10, height=self.tile_size//30)
                row.append(btn)
            self.buttons.append(row)
        for i in range(3):
            self.frame.grid_rowconfigure(i, weight=1, minsize=self.tile_size)
            self.frame.grid_columnconfigure(i, weight=1, minsize=self.tile_size)

        control = tk.Frame(self.master, bg="#222")
        control.pack(pady=5)
        self.scramble_btn = tk.Button(control, text="Scramble", command=self.scramble, width=10)
        self.scramble_btn.pack(side=tk.LEFT, padx=5)
        self.solve_btn = tk.Button(control, text="Solve", command=self.solve, width=10)
        self.solve_btn.pack(side=tk.LEFT, padx=5)
        self.random_btn = tk.Button(control, text="Random", command=self.random_scramble, width=10)
        self.random_btn.pack(side=tk.LEFT, padx=5)
        self.undo_btn = tk.Button(control, text="Undo", command=self.undo, width=10)
        self.undo_btn.pack(side=tk.LEFT, padx=5)
        self.redo_btn = tk.Button(control, text="Redo", command=self.redo, width=10)
        self.redo_btn.pack(side=tk.LEFT, padx=5)

        # Difficulty selector
        tk.Label(control, text="Difficulty:", bg="#222", fg="#fff", font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
        self.difficulty_menu = tk.OptionMenu(control, self.difficulty, "Easy", "Medium", "Hard")
        self.difficulty_menu.config(width=8)
        self.difficulty_menu.pack(side=tk.LEFT, padx=5)

        self.leaderboard_btn = tk.Button(control, text="Leaderboard", command=self.show_leaderboard, width=12)
        self.leaderboard_btn.pack(side=tk.LEFT, padx=5)

        info = tk.Frame(self.master, bg="#222")
        info.pack(pady=5)
        self.move_label = tk.Label(info, text="Moves: 0", font=('Arial', 14), bg="#222", fg="#fff")
        self.move_label.pack(side=tk.LEFT, padx=10)
        self.time_label = tk.Label(info, text="Time: 0.0s", font=('Arial', 14), bg="#222", fg="#fff")
        self.time_label.pack(side=tk.LEFT, padx=10)
        self.status_label = tk.Label(info, text="", font=('Arial', 14, 'bold'), bg="#222", fg="#90ee90")
        self.status_label.pack(side=tk.LEFT, padx=10)

    def update_grid(self):
        for i in range(3):
            for j in range(3):
                val = self.state[i*3 + j]
                btn = self.buttons[i][j]
                btn['image'] = ''
                if val == 0:
                    btn['text'] = ''
                    btn['bg'] = "#d3d3d3"
                    btn['activebackground'] = "#d3d3d3"
                else:
                    btn['text'] = str(val)
                    btn['bg'] = "#f0e68c"
                    btn['activebackground'] = "#ffe4b5"
        self.move_label['text'] = f"Moves: {self.move_count}"
        self.time_label['text'] = f"Time: {self.elapsed_time:.1f}s"
        self.status_label['text'] = ""
        if self.state == self.env.goal:
            self.status_label['text'] = "Solved!"
            self.stop_timer()
            self.save_leaderboard_entry()

    def start_timer(self):
        if not self.timer_running:
            self.start_time = time.time() - self.elapsed_time
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            self.elapsed_time = time.time() - self.start_time
            self.time_label['text'] = f"Time: {self.elapsed_time:.1f}s"
            self.timer_id = self.master.after(100, self.update_timer)

    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False
            if self.timer_id:
                self.master.after_cancel(self.timer_id)
                self.timer_id = None

    def reset_timer(self):
        self.stop_timer()
        self.elapsed_time = 0
        self.time_label['text'] = "Time: 0.0s"

    def get_scramble_depth(self):
        diff = self.difficulty.get()
        if diff == "Easy":
            return 15
        elif diff == "Medium":
            return 30
        else:
            return 50

    def scramble(self):
        if self.solving: return
        self.state = self.env.goal
        depth = self.get_scramble_depth()
        for _ in range(depth):
            neighbors = get_neighbors(self.state, 3)
            self.state = random.choice(neighbors)
        self.move_count = 0
        self.history = [self.state]
        self.future = []
        self.reset_timer()
        self.update_grid()
        self.start_timer()

    def random_scramble(self):
        if self.solving: return
        while True:
            perm = list(range(9))
            random.shuffle(perm)
            if self.env._is_solvable(perm):
                self.state = tuple(perm)
                break
        self.move_count = 0
        self.history = [self.state]
        self.future = []
        self.reset_timer()
        self.update_grid()
        self.start_timer()

    def solve(self):
        if self.solving: return
        self.solving = True
        self.disable_controls()
        def animate():
            solution = a_star(self.state, self.env.goal)
            if not solution:
                self.status_label['text'] = "No solution found."
                self.solving = False
                self.enable_controls()
                return
            for s in solution[1:]:
                self.state = s
                self.move_count += 1
                self.history.append(self.state)
                self.future = []
                self.update_grid()
                self.master.update()
                time.sleep(0.25)
            self.solving = False
            self.enable_controls()
        Thread(target=animate).start()

    def move_tile(self, x, y):
        if self.solving: return
        zero_idx = self.state.index(0)
        zx, zy = divmod(zero_idx, 3)
        if abs(zx - x) + abs(zy - y) == 1:
            lst = list(self.state)
            idx = x * 3 + y
            lst[zero_idx], lst[idx] = lst[idx], lst[zero_idx]
            self.state = tuple(lst)
            self.move_count += 1
            self.history.append(self.state)
            self.future = []
            if self.move_count == 1:
                self.start_timer()
            self.update_grid()

    def undo(self):
        if self.solving: return
        if len(self.history) > 1:
            self.future.append(self.history.pop())
            self.state = self.history[-1]
            self.move_count = max(0, self.move_count - 1)
            self.update_grid()

    def redo(self):
        if self.solving: return
        if self.future:
            self.state = self.future.pop()
            self.history.append(self.state)
            self.move_count += 1
            self.update_grid()

    def disable_controls(self):
        self.scramble_btn['state'] = tk.DISABLED
        self.solve_btn['state'] = tk.DISABLED
        self.random_btn['state'] = tk.DISABLED
        self.undo_btn['state'] = tk.DISABLED
        self.redo_btn['state'] = tk.DISABLED
        self.difficulty_menu['state'] = tk.DISABLED
        for row in self.buttons:
            for btn in row:
                btn['state'] = tk.DISABLED

    def enable_controls(self):
        self.scramble_btn['state'] = tk.NORMAL
        self.solve_btn['state'] = tk.NORMAL
        self.random_btn['state'] = tk.NORMAL
        self.undo_btn['state'] = tk.NORMAL
        self.redo_btn['state'] = tk.NORMAL
        self.difficulty_menu['state'] = tk.NORMAL
        for row in self.buttons:
            for btn in row:
                btn['state'] = tk.NORMAL

    def save_leaderboard_entry(self):
        if self.move_count == 0 or self.elapsed_time < 0.01:
            return
        entry = {
            'moves': self.move_count,
            'time': round(self.elapsed_time, 2),
            'difficulty': self.difficulty.get(),
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        entries = self.load_leaderboard()
        entries.append(entry)
        entries.sort(key=lambda e: (e['moves'], e['time']))
        entries = entries[:self.LEADERBOARD_SIZE]
        with open(self.LEADERBOARD_FILE, 'w') as f:
            for e in entries:
                f.write(f"{e['moves']},{e['time']},{e['difficulty']},{e['date']}\n")

    def load_leaderboard(self):
        entries = []
        if os.path.exists(self.LEADERBOARD_FILE):
            with open(self.LEADERBOARD_FILE, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 4:
                        moves, time_val, diff, date = parts
                        entries.append({
                            'moves': int(moves),
                            'time': float(time_val),
                            'difficulty': diff,
                            'date': date
                        })
        return entries

    def show_leaderboard(self):
        entries = self.load_leaderboard()
        win = tk.Toplevel(self.master)
        win.title("Leaderboard")
        win.configure(bg="#222")
        tk.Label(win, text="Top Results", font=('Arial', 16, 'bold'), bg="#222", fg="#fff").pack(pady=8)
        if not entries:
            tk.Label(win, text="No results yet.", font=('Arial', 12), bg="#222", fg="#fff").pack(pady=8)
        else:
            for idx, e in enumerate(entries, 1):
                tk.Label(win, text=f"{idx}. {e['moves']} moves, {e['time']}s, {e['difficulty']}, {e['date']}",
                         font=('Arial', 12), bg="#222", fg="#fff").pack(anchor='w', padx=20)
        tk.Button(win, text="Close", command=win.destroy).pack(pady=10)

if __name__ == '__main__':
    root = tk.Tk()
    gui = EightPuzzleGUI(root)
    root.mainloop() 
