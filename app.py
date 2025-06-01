import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_openai import OpenAI
import re

# === CONFIG ===
api_key = st.secrets["OPENAI_API_KEY"]
llm = OpenAI(temperature=0.7, openai_api_key=api_key, max_tokens=1000)

# Set macro goals (customize if needed)
TARGET_CALORIES = 1800
TARGET_PROTEIN = 130

# === GPT FUNCTIONS ===
def generate_meal_plan(goal: str) -> str:
    prompt = (
        f"Create a high-protein, gluten-free meal plan for someone with this fitness goal: {goal}.\n"
        "Include breakfast, lunch, dinner, and a snack. Show calories and protein for each meal."
    )
    return llm.invoke(prompt)

def generate_workout_plan(goal: str) -> str:
    prompt = (
        f"Create a 45-minute glute- and core-focused workout for someone with this goal: {goal}.\n"
        "Include sets, reps, rest time, and the muscles being worked."
    )
    return llm.invoke(prompt)

# === MACRO EXTRACTOR ===
def extract_macros(meal_text: str):
    # Remove lines that include "Total:" or "Overall daily total"
    lines = meal_text.splitlines()
    filtered_lines = [
        line for line in lines
        if "Total:" not in line and "Overall daily total" not in line
    ]

    calorie_matches = re.findall(r"(\d+)\s*calories", "\n".join(filtered_lines))
    protein_matches = re.findall(r"(\d+)\s*g protein", "\n".join(filtered_lines))

    total_calories = sum(map(int, calorie_matches))
    total_protein = sum(map(int, protein_matches))

    return total_calories, total_protein

# === STREAMLIT UI ===
st.set_page_config(page_title="NutriAgent", layout="centered")
st.title("🥦 NutriAgent: Your AI Fitness Coach")
st.caption("Get a meal + workout plan instantly based on your goals.")

goal_input = st.text_area("💬 What's your fitness goal? (e.g. grow glutes, stay lean, gluten-free meals)", height=100)

if st.button("Generate My Plan"):
    with st.spinner("Thinking..."):
        meal_plan = generate_meal_plan(goal_input)
        workout_plan = generate_workout_plan(goal_input)
        total_calories, total_protein = extract_macros(meal_plan)

        response = f"Meal Plan:\n{meal_plan}\n\nWorkout Plan:\n{workout_plan}"

    st.success("Here’s your personalized plan:")
    st.markdown("### 🤖💪 Powered by GPT + LangChain")
    st.download_button("Download Plan as .txt", response, file_name="my_fitness_plan.txt")

    # === Meal Plan Display ===
    st.subheader("🥗 Meal Plan")
    st.markdown(meal_plan)

    # === Macro Summary Bars ===
    st.markdown(f"**📊 Total Calories:** {total_calories} / {TARGET_CALORIES}")
    st.progress(min(total_calories / TARGET_CALORIES, 1.0))

    st.markdown(f"**💪 Total Protein:** {total_protein}g / {TARGET_PROTEIN}g")
    st.progress(min(total_protein / TARGET_PROTEIN, 1.0))

    # === Workout Plan Display ===
    st.subheader("🏋️ Workout Plan")
    st.markdown(workout_plan)