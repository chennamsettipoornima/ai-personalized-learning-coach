
import streamlit as st

from database import (
    init_db,
    save_plan,
    get_latest_plan,
    save_attempt,
    get_attempts,
    get_topic_summary
)

from learning_plan import generate_learning_plan
from quiz_manager import generate_quiz, evaluate_quiz


# Page configuration
st.set_page_config(
    page_title="AI Personalized Learning Coach",
    page_icon="🎓",
    layout="wide"
)

# Initialize database
init_db()

# Session state
if "active_plan" not in st.session_state:
    st.session_state.active_plan = get_latest_plan()

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None


# Application heading
st.title("🎓 AI Personalized Learning Coach")

st.write(
    "Your personal AI learning assistant. "
    "Generate study plans, practice quizzes and track your progress."
)

# Navigation
setup_tab, plan_tab, quiz_tab, dashboard_tab = st.tabs([
    "🏠 Learner Setup",
    "📚 Study Plan",
    "📝 Practice Quiz",
    "📊 Progress Dashboard"
])


# ----------------------------------
# TAB 1: LEARNER SETUP
# ----------------------------------

with setup_tab:

    st.header("Create Your Learning Profile")

    with st.form("learner_form"):

        subject = st.text_input(
            "What subject do you want to learn?",
            placeholder="Example: Python"
        )

        goal = st.text_area(
            "What is your learning goal?",
            placeholder="Example: Learn Python fundamentals"
        )

        level = st.selectbox(
            "Current Knowledge Level",
            ["Beginner", "Intermediate", "Advanced"]
        )

        duration = st.number_input(
            "Learning Duration (Days)",
            min_value=1,
            max_value=90,
            value=7
        )

        daily_time = st.number_input(
            "Daily Study Time (Minutes)",
            min_value=15,
            max_value=480,
            value=45
        )

        submitted = st.form_submit_button(
            "Generate My Learning Plan",
            type="primary"
        )

    if submitted:

        if not subject.strip() or not goal.strip():
            st.error("Please enter both subject and learning goal.")

        else:
            try:
                with st.spinner("AI is creating your personalized plan..."):

                    plan = generate_learning_plan(
                        subject.strip(),
                        goal.strip(),
                        level,
                        int(duration),
                        int(daily_time)
                    )

                    plan_id = save_plan(
                        subject.strip(),
                        goal.strip(),
                        level,
                        int(duration),
                        int(daily_time),
                        plan
                    )

                    st.session_state.active_plan = {
                        "plan_id": plan_id,
                        "plan": plan,
                        "subject": subject.strip(),
                        "level": level
                    }

                    st.session_state.quiz = None
                    st.session_state.quiz_result = None

                st.success("Your personalized learning plan is ready!")

            except Exception as error:
                st.error(f"Unable to generate plan: {error}")


# ----------------------------------
# TAB 2: STUDY PLAN
# ----------------------------------

with plan_tab:

    st.header("📚 Your Personalized Study Plan")

    active = st.session_state.active_plan

    if active:

        st.subheader(f"Subject: {active['subject']}")

        for day in active["plan"]["days"]:

            with st.expander(
                f"Day {day['day']}: {day['topic']}",
                expanded=False
            ):

                st.write("**Learning Objective:**")
                st.write(day["objective"])

                st.write(
                    f"**Estimated Study Time:** {day['minutes']} minutes"
                )

                st.write("**Practice Activities:**")

                for activity in day["activities"]:
                    st.write(f"- {activity}")

    else:
        st.info("Create your learning profile to generate a study plan.")


# ----------------------------------
# TAB 3: PRACTICE QUIZ
# ----------------------------------

with quiz_tab:

    st.header("📝 Topic-Based Practice Quiz")

    active = st.session_state.active_plan

    if active:

        days = active["plan"]["days"]

        topics = [day["topic"] for day in days]

        selected_topic = st.selectbox(
            "Choose a topic",
            topics
        )

        if st.button("Generate Quiz", type="primary"):

            try:
                with st.spinner("Generating your quiz..."):

                    quiz = generate_quiz(
                        active["subject"],
                        selected_topic,
                        active["level"]
                    )

                    st.session_state.quiz = {
                        "topic": selected_topic,
                        "questions": quiz["questions"],
                        "plan_id": active["plan_id"]
                    }

                    st.session_state.quiz_result = None

            except Exception as error:
                st.error(f"Quiz generation failed: {error}")

        quiz_data = st.session_state.quiz

        if quiz_data and quiz_data["topic"] == selected_topic:

            st.divider()

            st.subheader(f"Quiz: {selected_topic}")

            with st.form("quiz_form"):

                answers = {}

                for index, question in enumerate(
                    quiz_data["questions"]
                ):

                    st.write(
                        f"**Q{index + 1}. {question['question']}**"
                    )

                    answers[index] = st.radio(
                        f"Select your answer for Question {index + 1}",
                        question["options"],
                        index=None,
                        key=f"answer_{index}"
                    )

                submitted = st.form_submit_button(
                    "Submit Answers",
                    type="primary"
                )

            if submitted:

                if any(answer is None for answer in answers.values()):

                    st.warning("Please answer all five questions.")

                else:

                    try:
                        answer_indexes = {}

                        for index, question in enumerate(
                            quiz_data["questions"]
                        ):
                            answer_indexes[index] = (
                                question["options"].index(
                                    answers[index]
                                )
                            )

                        result = evaluate_quiz(
                            quiz_data["questions"],
                            answer_indexes
                        )

                        save_attempt(
                            quiz_data["plan_id"],
                            quiz_data["topic"],
                            result["score"],
                            result["total"],
                            result["percentage"]
                        )

                        st.session_state.quiz_result = result

                    except Exception as error:
                        st.error(f"Unable to evaluate quiz: {error}")

            result = st.session_state.quiz_result

            if result and quiz_data["topic"] == selected_topic:

                st.divider()

                st.subheader("📋 Your Quiz Results")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Score",
                    f"{result['score']}/{result['total']}"
                )

                col2.metric(
                    "Percentage",
                    f"{result['percentage']:.0f}%"
                )

                col3.metric(
                    "Correct Answers",
                    result["score"]
                )

                st.write("### Answer Explanations")

                for index, feedback in enumerate(
                    result["feedback"]
                ):

                    if feedback["is_correct"]:
                        st.success(
                            f"Q{index + 1}: Correct answer!"
                        )
                    else:
                        st.error(
                            f"Q{index + 1}: Incorrect answer."
                        )

                    st.write(
                        "Correct answer: "
                        + quiz_data["questions"][index]["options"][
                            feedback["correct"]
                        ]
                    )

                    st.write(
                        "Explanation: " + feedback["explanation"]
                    )

                st.info(result["recommendation"])

    else:
        st.info("Generate a learning plan before taking a quiz.")


# ----------------------------------
# TAB 4: PROGRESS DASHBOARD
# ----------------------------------

with dashboard_tab:

    st.header("📊 Learning Progress Dashboard")

    active = st.session_state.active_plan

    if active:

        topics = [
            day["topic"]
            for day in active["plan"]["days"]
        ]

        summary = get_topic_summary()

        completed = 0
        weak = 0

        for topic in topics:

            if topic in summary:

                percentage = summary[topic]["latest_percentage"]

                if percentage >= 80:
                    completed += 1

                elif percentage < 60:
                    weak += 1

        pending = len(topics) - completed

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Topics", len(topics))
        col2.metric("Strong Topics", completed)
        col3.metric("Weak Topics", weak)
        col4.metric("Pending Topics", pending)

        st.subheader("Topic Progress")

        for topic in topics:

            if topic in summary:

                percentage = summary[topic]["latest_percentage"]

                st.write(f"**{topic}**")

                st.progress(
                    int(max(0, min(100, percentage)))
                )

                st.caption(
                    f"Latest score: {percentage:.0f}% | "
                    f"Attempts: {summary[topic]['attempts']}"
                )

                if percentage < 60:
                    st.warning("Recommended: Revise this topic.")

                elif percentage < 80:
                    st.info("Recommended: More practice.")

                else:
                    st.success("Good performance! Consider the next topic.")

            else:
                st.write(f"**{topic}** - Not attempted yet")

        st.subheader("Learning History")

        attempts = get_attempts()

        if attempts:

            st.dataframe(
                [
                    {
                        "Topic": row[0],
                        "Score": f"{row[1]}/{row[2]}",
                        "Percentage": f"{row[3]:.0f}%",
                        "Date": row[4]
                    }
                    for row in attempts
                ],
                use_container_width=True
            )

        else:
            st.info("No quiz attempts yet.")

    else:
        st.info("Generate your learning plan to view progress.")
