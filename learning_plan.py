
from ai_service import generate_json


def generate_learning_plan(subject, goal, level, duration, daily_time):

    prompt = f"""
    You are an expert AI learning coach.

    Create a personalized learning plan using these details:

    Subject: {subject}
    Goal: {goal}
    Current Level: {level}
    Duration: {duration} days
    Daily Study Time: {daily_time} minutes

    Requirements:
    1. Create exactly {duration} days.
    2. Arrange topics in a logical learning order.
    3. Match the difficulty to the student's level.
    4. Keep daily estimated time within {daily_time} minutes.
    5. Include objectives and practical activities.

    Return valid JSON only in this format:

    {{
      "days": [
        {{
          "day": 1,
          "topic": "Topic name",
          "objective": "Learning objective",
          "minutes": 45,
          "activities": [
            "Read the concepts",
            "Practice examples"
          ]
        }}
      ]
    }}
    """

    data = generate_json(prompt)

    if not isinstance(data, dict):
        raise ValueError("Invalid learning plan format.")

    days = data.get("days")

    if not isinstance(days, list) or len(days) != duration:
        raise ValueError("Learning plan has an incorrect number of days.")

    for index, day in enumerate(days, start=1):
        if not isinstance(day, dict):
            raise ValueError("Invalid day format.")

        if day.get("day") != index:
            raise ValueError("Day numbers must be sequential.")

        if not all(day.get(key) for key in
                   ["topic", "objective", "minutes", "activities"]):
            raise ValueError("Missing information in learning plan.")

        if not isinstance(day["minutes"], int):
            raise ValueError("Study time must be an integer.")

        if day["minutes"] <= 0 or day["minutes"] > daily_time:
            raise ValueError("Invalid daily study time.")

        if not isinstance(day["activities"], list):
            raise ValueError("Activities must be a list.")

    return data
