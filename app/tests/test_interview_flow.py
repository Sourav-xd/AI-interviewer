# app/tests/test_interview_flow.py
from IPython.display import Image, display

from app.agents.orchestrator import InterviewOrchestrator
from app.services.memory_service import memory_service

def run_manual_test():
    orchestrator = InterviewOrchestrator()
    candidate_id = "test_candidate_1"

    print("\n--- ROUND 1 ---")
    response = orchestrator.run_step(
        candidate_id=candidate_id,
        candidate_answer="Python is a programming language.",
        confidence_score=0.7,
        emotion_state="calm"
    )
    print(response)

    print("\n--- ROUND 2 ---")
    response = orchestrator.run_step(
        candidate_id=candidate_id,
        candidate_answer="It supports OOP and scripting.",
        confidence_score=0.6,
        emotion_state="calm"
    )
    print(response)

    print("\n--- ROUND 3 ---")
    response = orchestrator.run_step(
        candidate_id=candidate_id,
        candidate_answer="I am not sure about decorators.",
        confidence_score=0.4,
        emotion_state="nervous"
    )
    print(response)

    print("\n--- MEMORY DUMP ---")
    print("Stored interactions:")
    for item in memory_service.metadata:
        print(item)

    print("\nCandidate profile summary:")
    print(memory_service.summarize_candidate_profile())

    print("\nWeak topics:")
    print(memory_service.get_weak_topics())

    # print(orchestrator.graph.get_graph().draw_mermaid())

    

if __name__ == "__main__":
    run_manual_test()


