# Student Performance Prediction

A Flask and SQLite learning portal for Muthayammal Engineering College. Students can study five programming courses, track active study time, take individual quizzes, and review their performance.

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Start the server: `python app.py`
4. Open `http://127.0.0.1:5000`.

The SQLite database (`student_performance.db`) is created automatically when the app starts. A register number identifies a student, so returning students can sign in with the same number. Active page time is recorded while the browser tab is visible. A course quiz unlocks after five minutes of tracked study, and a mark of at least 7/10 completes the course.

Set `FLASK_SECRET_KEY` to a private random value before deploying. The built-in key is for local development only. The welcome page uses an original illustration; replace it with an approved college image if one is available.
