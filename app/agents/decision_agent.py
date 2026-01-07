#decision_agent.py
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash-lite",
#     temperature=0.1,
#     max_output_tokens=100
# )

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.1,
    max_tokens=100,
)


class DecisionOutput(BaseModel):
    decision: str

#json_parser = JsonOutputParser()
json_parser = PydanticOutputParser(pydantic_object=DecisionOutput)

template= """
You are an interview decision engine for a Level-0 technical interview.

Your task:
Decide the NEXT ACTION the interviewer should take.

You must choose ONLY ONE of the following decisions:
- ASK_FOLLOWUP
- NEXT_TOPIC
- INCREASE_DIFFICULTY
- END_INTERVIEW

Decision rules (internal, do NOT explain):
- If interview_round >= max_rounds → END_INTERVIEW
- If correctness_score is low OR depth_level is "poor" → ASK_FOLLOWUP
- If follow_up_needed is true → ASK_FOLLOWUP
- If correctness_score is high AND depth_level is "good" → INCREASE_DIFFICULTY
- If candidate seems nervous or confidence is low → ASK_FOLLOWUP (simpler)
- Otherwise → NEXT_TOPIC

Inputs:
Knowledge Evaluation:
{knowledge_evaluation}

Confidence Score:
{confidence_score}

Emotion State:
{emotion_state}

Topics Covered:
{topics_covered}

Interview Round:
{interview_round}

Maximum Rounds:
{max_rounds}

Output rules:
- Output JSON only
- Do NOT add explanations
- Use exactly one decision value

{format_instructions}
"""

DECISION_PROMPT = PromptTemplate(
    input_variables=[
        "knowledge_evaluation",
        "confidence_score",
        "emotion_state",
        "topics_covered",
        "interview_round",
        "max_rounds"
    ],
    partial_variables={
        "format_instructions": json_parser.get_format_instructions()
    },
    template=template
)

decision_chain = DECISION_PROMPT | llm | json_parser

def decide_next_step(context: dict)-> dict:
    decision = decision_chain.invoke(
        {
        "knowledge_evaluation": context.get("knowledge_evaluation", {}),
        "confidence_score": context.get("confidence_score", 0.5),
        "emotion_state": context.get("emotion_state", "calm"),
        "topics_covered": context.get("topics_covered", []),
        "interview_round": context.get("interview_round", 1),
        "max_rounds": context.get("max_rounds", 5)
        }
    )

    return decision




# TESTING THE AGENT

# test_context = {
#     "knowledge_evaluation": {
#         "correctness_score": 0.4,
#         "depth_level": "poor",
#         "follow_up_needed": True
#     },
#     "confidence_score": 0.6,
#     "emotion_state": "calm",
#     "topics_covered": ["Python basics"],
#     "interview_round": 2,
#     "max_rounds": 5
# }

# print(decide_next_step(test_context))
