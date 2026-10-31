
from ai_service import generate_json


def generate_quiz(subject, topic, level):

    prompt = f"""
    You are an educational quiz creator.

    Subject: {subject}
    Topic: {topic}
    Student Level: {level}

    Generate exactly 5 multiple-choice questions.

    Each question must have:
    - question
    - options: exactly 4 options
    - answer_index: correct option index (0, 1, 2 or 3)
    - explanation: explain why the answer is correct

    Keep the questions appropriate for the student's level.

    Return valid JSON only:

    {{
      "questions": [
        {{
          "question": "What is Python?",
          "options": [
            "A programming language",
            "An operating system",
            "A database",
            "A browser"
          ],
          "answer_index": 0,
          "explanation": "Python is a programming language."
        }}
      ]
    }}
    """

    data = generate_json(prompt)

    if not isinstance(data, dict):
        raise ValueError("Invalid quiz response.")

    questions = data.get("questions")

    if not isinstance(questions, list) or len(questions) != 5:
        raise ValueError("Quiz must contain exactly 5 questions.")

    for question in questions:
        if not isinstance(question, dict):
            raise ValueError("Invalid question format.")

        if not all(question.get(key) for key in
                   ["question", "options", "explanation"]):
            raise ValueError("Missing question information.")

        options = question["options"]
        answer = question.get("answer_index")

        if not isinstance(options, list) or len(options) != 4:
            raise ValueError("Each question needs 4 options.")

        if not isinstance(answer, int) or isinstance(answer, bool):
            raise ValueError("Invalid answer index.")

        if answer not in range(4):
            raise ValueError("Correct answer must be between 0 and 3.")

    return data


def evaluate_quiz(questions, answers):

    score = 0
    feedback = []

    for index, question in enumerate(questions):
        correct_answer = question["answer_index"]
        selected_answer = answers.get(index)

        is_correct = selected_answer == correct_answer

        if is_correct:
            score += 1

        feedback.append({
            "question": question["question"],
            "selected": selected_answer,
            "correct": correct_answer,
            "is_correct": is_correct,
            "explanation": question["explanation"]
        })

    percentage = (score / len(questions)) * 100

    if percentage < 60:
        recommendation = "Revise this topic and take another practice quiz."
    elif percentage < 80:
        recommendation = "Good effort! Practice a few more questions."
    else:
        recommendation = "Strong performance! Try the next topic or harder questions."

    return {
        "score": score,
        "total": len(questions),
        "percentage": percentage,
        "feedback": feedback,
        "recommendation": recommendation
    }
