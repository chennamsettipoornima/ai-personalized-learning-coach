
import sqlite3
import json

DB_NAME = "learning_coach.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS learners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                goal TEXT,
                level TEXT,
                duration INTEGER,
                daily_time INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                learner_id INTEGER,
                plan_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (learner_id) REFERENCES learners(id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER,
                topic TEXT,
                score INTEGER,
                total INTEGER,
                percentage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES plans(id)
            )
        """)


def save_plan(subject, goal, level, duration, daily_time, plan):

    with get_connection() as conn:

        cursor = conn.execute("""
            INSERT INTO learners
            (subject, goal, level, duration, daily_time)
            VALUES (?, ?, ?, ?, ?)
        """, (subject, goal, level, duration, daily_time))

        learner_id = cursor.lastrowid

        cursor = conn.execute("""
            INSERT INTO plans (learner_id, plan_json)
            VALUES (?, ?)
        """, (learner_id, json.dumps(plan)))

        return cursor.lastrowid


def get_latest_plan():

    with get_connection() as conn:
        row = conn.execute("""
            SELECT plans.id, plans.plan_json,
                   learners.subject, learners.level
            FROM plans
            JOIN learners ON plans.learner_id = learners.id
            ORDER BY plans.id DESC
            LIMIT 1
        """).fetchone()

    if row:
        return {
            "plan_id": row[0],
            "plan": json.loads(row[1]),
            "subject": row[2],
            "level": row[3]
        }

    return None


def save_attempt(plan_id, topic, score, total, percentage):

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO attempts
            (plan_id, topic, score, total, percentage)
            VALUES (?, ?, ?, ?, ?)
        """, (plan_id, topic, score, total, percentage))


def get_attempts():

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT topic, score, total, percentage, created_at
            FROM attempts
            ORDER BY id DESC
        """).fetchall()

    return rows


def get_topic_summary():

    attempts = get_attempts()
    summary = {}

    for topic, score, total, percentage, date in attempts:
        if topic not in summary:
            summary[topic] = {
                "attempts": 0,
                "latest_score": score,
                "latest_total": total,
                "latest_percentage": percentage
            }

        summary[topic]["attempts"] += 1

    return summary
