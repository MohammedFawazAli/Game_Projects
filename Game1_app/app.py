import streamlit as st
import numpy as np
import random
import time
import os
import datetime
from collections import deque

# --- 8-Puzzle Logic (from learning.py) ---
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

# --- A* Search Implementation ---
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

# --- Streamlit App ---
st.set_page_config(page_title="8-Puzzle Solver", layout="centered")
st.title("8-Puzzle Solver 🧩")

# --- Session State Initialization ---
def init_state():
    if 'env' not in st.session_state:
        st.session_state.env = EightPuzzleEnv()
    if 'state' not in st.session_state:
        st.session_state.state = st.session_state.env.goal
    if 'move_count' not in st.session_state:
        st.session_state.move_count = 0
    if 'history' not in st.session_state:
        st.session_state.history = [st.session_state.env.goal]
    if 'future' not in st.session_state:
        st.session_state.future = []
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'elapsed_time' not in st.session_state:
        st.session_state.elapsed_time = 0.0
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = 'Medium'
    if 'leaderboard' not in st.session_state:
        st.session_state.leaderboard = []

init_state()

def get_scramble_depth():
    diff = st.session_state.difficulty
    if diff == "Easy":
        return 15
    elif diff == "Medium":
        return 30
    else:
        return 50

def scramble():
    st.session_state.state = st.session_state.env.goal
    depth = get_scramble_depth()
    for _ in range(depth):
        neighbors = get_neighbors(st.session_state.state, 3)
        st.session_state.state = random.choice(neighbors)
    st.session_state.move_count = 0
    st.session_state.history = [st.session_state.state]
    st.session_state.future = []
    st.session_state.elapsed_time = 0.0
    st.session_state.start_time = time.time()
    st.session_state.timer_running = True

def random_scramble():
    while True:
        perm = list(range(9))
        random.shuffle(perm)
        if st.session_state.env._is_solvable(perm):
            st.session_state.state = tuple(perm)
            break
    st.session_state.move_count = 0
    st.session_state.history = [st.session_state.state]
    st.session_state.future = []
    st.session_state.elapsed_time = 0.0
    st.session_state.start_time = time.time()
    st.session_state.timer_running = True

def move_tile(idx):
    zero_idx = st.session_state.state.index(0)
    zx, zy = divmod(zero_idx, 3)
    x, y = divmod(idx, 3)
    if abs(zx - x) + abs(zy - y) == 1:
        lst = list(st.session_state.state)
        lst[zero_idx], lst[idx] = lst[idx], lst[zero_idx]
        st.session_state.state = tuple(lst)
        st.session_state.move_count += 1
        st.session_state.history.append(st.session_state.state)
        st.session_state.future = []
        if st.session_state.move_count == 1:
            st.session_state.start_time = time.time()
            st.session_state.timer_running = True

def undo():
    if len(st.session_state.history) > 1:
        st.session_state.future.append(st.session_state.history.pop())
        st.session_state.state = st.session_state.history[-1]
        st.session_state.move_count = max(0, st.session_state.move_count - 1)

def redo():
    if st.session_state.future:
        st.session_state.state = st.session_state.future.pop()
        st.session_state.history.append(st.session_state.state)
        st.session_state.move_count += 1

def solve():
    solution = a_star(st.session_state.state, st.session_state.env.goal)
    if not solution:
        st.warning("No solution found.")
        return
    for s in solution[1:]:
        st.session_state.state = s
        st.session_state.move_count += 1
        st.session_state.history.append(st.session_state.state)
        st.session_state.future = []
        st.experimental_rerun()
        time.sleep(0.25)
    st.success("Solved!")
    st.session_state.timer_running = False
    save_leaderboard_entry()

def save_leaderboard_entry():
    if st.session_state.move_count == 0 or st.session_state.elapsed_time < 0.01:
        return
    entry = {
        'moves': st.session_state.move_count,
        'time': round(st.session_state.elapsed_time, 2),
        'difficulty': st.session_state.difficulty,
        'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    st.session_state.leaderboard.append(entry)
    st.session_state.leaderboard.sort(key=lambda e: (e['moves'], e['time']))
    st.session_state.leaderboard = st.session_state.leaderboard[:10]

def update_timer():
    if st.session_state.timer_running:
        st.session_state.elapsed_time = time.time() - st.session_state.start_time
        st.experimental_rerun()

# --- UI Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Puzzle Board")
    grid = np.array(st.session_state.state).reshape((3, 3))
    for i in range(3):
        cols = st.columns(3)
        for j in range(3):
            val = grid[i, j]
            if val == 0:
                cols[j].button(" ", key=f"tile_{i}_{j}", disabled=True)
            else:
                if cols[j].button(str(val), key=f"tile_{i}_{j}"):
                    move_tile(i*3 + j)
                    st.experimental_rerun()
    st.write(f"Moves: {st.session_state.move_count}")
    st.write(f"Time: {st.session_state.elapsed_time:.1f}s")
    if st.session_state.state == st.session_state.env.goal:
        st.success("Solved!")
        st.session_state.timer_running = False
        save_leaderboard_entry()

with col2:
    st.subheader("Controls")
    if st.button("Scramble"):
        scramble()
        st.experimental_rerun()
    if st.button("Random"):
        random_scramble()
        st.experimental_rerun()
    if st.button("Solve"):
        solve()
        st.experimental_rerun()
    st.button("Undo", on_click=undo)
    st.button("Redo", on_click=redo)
    st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key='difficulty')
    st.subheader("Leaderboard")
    if st.session_state.leaderboard:
        for idx, e in enumerate(st.session_state.leaderboard, 1):
            st.write(f"{idx}. {e['moves']} moves, {e['time']}s, {e['difficulty']}, {e['date']}")
    else:
        st.write("No results yet.")

# --- Timer Update ---
if st.session_state.timer_running:
    update_timer() 