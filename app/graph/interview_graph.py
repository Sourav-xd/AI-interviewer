#interview_graph.py
from langgraph.graph import StateGraph, END
from app.models.interview_state import InterviewState , InterviewStatus , DecisionType
from app.agents.evaluation_agent import evaluate_knowledge
from app.agents.decision_agent import decide_next_step
from app.agents.question_agent import generate_question


# NODE 1 : evaluate answer
def evaluate_answer_node(state: InterviewState)-> InterviewState:
    evaluation = evaluate_knowledge(
        {
            "question": state.current_question,
            "answer": state.candidate_answer
        }
    )

    #state.knowledge_evaluation = evaluation
    state.knowledge_evaluation = evaluation.model_dump()
    
    for topic in state.knowledge_evaluation.get("detected_topics", []):
        if topic not in state.topics_covered:
            state.topics_covered.append(topic)

    state.interview_round += 1

    return state

# NODE 2 : decision making
def decision_node(state: InterviewState)-> InterviewState:

    if state.interview_round >= state.max_rounds:
        state.decision = DecisionType.END_INTERVIEW
        return state

    decision_result = decide_next_step(
        {
            "knowledge_evaluation": state.knowledge_evaluation,
            "confidence_score": state.confidence_score,
            "emotion_state": state.emotion_state,
            "topics_covered": state.topics_covered,
            "interview_round": state.interview_round,
            "max_rounds": state.max_rounds
        }
    )

    # state.decision = DecisionType(decision_result["decision"])
    state.decision = DecisionType(decision_result.decision)
    return state

# NODE 3 : Question generation
def question_generation_node(state: InterviewState)-> InterviewState:
    question = generate_question(
        {
            "previous_questions": state.past_questions,
            "answer_summary": state.knowledge_evaluation,
            "covered_topics": state.topics_covered,
            "difficulty_level": "easy"  # can evolve later
        }
    )

    state.next_question = question
    state.current_question = question
    state.past_questions.append(question)

    return state

# NODE 4 : End interview
def end_interview_node(state: InterviewState)-> InterviewState:
    state.interview_status = InterviewStatus.ENDED
    state.next_question = None

    return state


#routes
def route_decision(state: InterviewState)-> str:
    if state.decision == DecisionType.END_INTERVIEW:
        return "end_interview"
    
    return "generate_question"


# Building graph and compilation
def build_interview_graph():
    graph = StateGraph(InterviewState)

    graph.add_node("evaluate_answer", evaluate_answer_node)
    graph.add_node("decide", decision_node)
    graph.add_node("generate_question", question_generation_node)
    graph.add_node("end_interview", end_interview_node)

    graph.set_entry_point("evaluate_answer")

    graph.add_edge("evaluate_answer", "decide")

    graph.add_conditional_edges(
        "decide",
        route_decision,
        {
            "generate_question": "generate_question",
            "end_interview": "end_interview"
        }
    )

    graph.add_edge("generate_question", END)
    graph.add_edge("end_interview", END)


    return graph.compile()




# from IPython.display import Image, display
# display(Image(graph.get_graph().draw_mermaid_png()))





    