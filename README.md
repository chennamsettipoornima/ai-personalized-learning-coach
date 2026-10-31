
# AI Personalized Learning Coach

## Project Overview

AI Personalized Learning Coach is a Generative AI
application that creates personalized study plans
and quizzes based on student requirements.

## Technologies Used

- Python
- Streamlit
- Gemini API
- SQLite
- python-dotenv

## Features

- Personalized learning plan generation
- Topic-based quiz generation
- Automatic answer evaluation
- Explanations and feedback
- Weak-topic identification
- Learning progress dashboard
- SQLite progress storage

## Installation

1. Clone or download the project.
2. Create a virtual environment.

   python -m venv .venv

3. Activate the environment.

   .\.venv\Scripts\Activate.ps1

4. Install dependencies.

   pip install -r requirements.txt

5. Create a .env file and add your Gemini API key.

   GEMINI_API_KEY=your_api_key_here

6. Run the application.

   streamlit run app.py

## Database

The application automatically creates
learning_coach.db to store learner profiles,
learning plans and quiz attempts.

## Project Goal

To provide students with an AI-powered
personalized learning experience.
