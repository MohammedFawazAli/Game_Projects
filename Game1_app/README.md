# 8-Puzzle Solver

This project is an interactive 8-puzzle solver with a graphical interface, now available as a web app using Streamlit!

## Features
- Play the 8-puzzle game in your browser
- Scramble, solve, undo, redo, and select difficulty
- Leaderboard for best results
- A* solver for instant solution

## Try it Online

- **Streamlit Cloud:** [Open App](https://YOUR-STREAMLIT-URL-HERE)
- **Hugging Face Spaces:** [Open App](https://huggingface.co/spaces/YOUR-SPACE-NAME)

## How to Run Locally

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```

## Deployment

- **Streamlit Cloud:**
  1. Push `app.py` and `requirements.txt` to your GitHub repo.
  2. Go to [Streamlit Cloud](https://share.streamlit.io/) and deploy your repo.

- **Hugging Face Spaces:**
  1. Create a new Space (select Streamlit as SDK).
  2. Upload `app.py` and `requirements.txt`.

## Files
- `app.py`: Streamlit web app
- `requirements.txt`: Python dependencies

## Original Desktop Version
The original Tkinter desktop version is in `learning.py`. 