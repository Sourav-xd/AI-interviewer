#evaluation_agent.py
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from pydantic import BaseModel



load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash-lite",
#     temperature=0.1,
#     max_output_tokens=300
# )

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.1,
    max_tokens=100,
)

class EvaluationOutput(BaseModel):
    correctness_score: float
    depth_level: str
    follow_up_needed: bool
    detected_topics: list[str]



#json_parser = PydanticOutputParser()


json_parser = PydanticOutputParser(pydantic_object=EvaluationOutput)

template = """
You are a strict technical evaluator conducting a Level-0 interview.

Your task:
Evaluate the candidate's answer ONLY for technical quality.

You must:
- Judge correctness of the answer
- Judge depth of understanding
- Detect key concepts mentioned
- Decide if a follow-up question is needed

Rules:
- Do NOT ask questions
- Do NOT give feedback or hints
- Do NOT explain your reasoning
- Do NOT mention emotions or confidence
- Be objective and strict
- Output JSON only

Evaluation guidelines:
- correctness_score: 
    1.0 = fully correct
    0.5 = partially correct
    0.0 = incorrect or irrelevant
- depth_level:
    "poor" = superficial / vague
    "basic" = correct but shallow
    "good" = clear and reasonably detailed
- follow_up_needed:
    true if answer is shallow or partially correct
    false if answer is sufficient for L0
- detected_topics:
  List the main technical topics explicitly mentioned.
  Examples: ["Python"], ["OOP"], ["JavaScript"]
  If none, return ["general"]

Question:
{question}

Candidate Answer:
{answer}

{format_instructions}
"""

EVALUATION_PROMPT = PromptTemplate(
    input_variables=["question" , "answer"],
    partial_variables={
        "format_instructions": json_parser.get_format_instructions()
    },
    template= template
)

evaluation_chain = EVALUATION_PROMPT | llm | json_parser

def evaluate_knowledge(context: dict) -> dict:
    
    evaluation =  evaluation_chain.invoke(
        {
            "question": context.get("question", ""),
            "answer": context.get("answer","")
        }
    )

    return evaluation


# test_context = {
#     "question": "What is Python?",
#     "answer": "Python is a programming language used for many things."
# }

# result = evaluate_knowledge(test_context)
# print(result)
