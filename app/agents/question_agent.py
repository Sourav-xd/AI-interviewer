#question_agent.py
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate 
from langchain_core.runnables import RunnableSequence
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash-lite",
#     temperature=0.35,
#     max_output_tokens=100
# )

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.35,
    max_tokens=100,
)


template = """
You are a human technical interviewer conducting a Level-0 interview.
Your task:
Ask the NEXT BEST interview question.

Rules you MUST follow:
- Ask ONLY ONE question.
- Keep it short and clear.
- Maintain a professional interview tone.
- Do NOT explain anything.
- Do NOT give feedback.
- Do NOT ask multiple questions.

Decision logic (use judgment, do NOT mention this):
- If the candidate's last answer was shallow or incomplete, ask a FOLLOW-UP question.
- Otherwise, move to a NEW topic that has NOT been covered yet.
- Match the question to the given difficulty level.

Context:
Previous Questions:
{previous_questions}

Candidate Answer Summary:
{answer_summary}

Topics Already Covered:
{covered_topics}

Difficulty Level:
{difficulty_level}

Output format:
<question only>
"""


QUESTION_PROMPT = PromptTemplate(
    input_variables=[
        "previous_questions",
        "answer_summary",
        "covered_topics",
        "difficulty_level"
    ],
    template=template
)

question_chain = QUESTION_PROMPT | llm

def generate_question(context: dict) -> str:

    response = question_chain.invoke({
        "previous_questions": context.get("previous_questions", []),
        "answer_summary": context.get("answer_summary", ""),
        "covered_topics": context.get("covered_topics", []),
        "difficulty_level": context.get("difficulty_level", "easy")
    })

    return response.content.strip()




# test_context = {
#     "previous_questions": ["What is Python?"],
#     "answer_summary": "Candidate gave a very basic definition.",
#     "covered_topics": ["Python basics"],
#     "difficulty_level": "easy"
# }

# print(generate_question(test_context))
