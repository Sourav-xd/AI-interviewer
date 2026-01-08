#orchestrator.py
from typing import Optional

from app.graph.interview_graph import build_interview_graph
from app.models.interview_state import InterviewState , create_initial_state
from app.services.memory_service import MemoryService




class InterviewOrchestrator:

    def __init__(self):
        #langgraph compilation (it is static)
        self.graph = build_interview_graph()
        self.sessions: dict[str, InterviewState] = {}
        self.memory = MemoryService()

    def _is_repeat_request(self, text: str) -> bool:
        text = text.lower()
        repeat_phrases = [
            "repeat",
            "say again",
            "can you repeat",
            "pardon",
            "didn't hear",
            "come again"
        ]
        return any(phrase in text for phrase in repeat_phrases)

    def run_step(
            self,
            candidate_id: str,
            candidate_answer: str,
            confidence_score: float = 0.5,
            emotion_state: str = "calm"
    ) -> dict:
        
        #loading the state
        if candidate_id not in self.sessions:
            self.sessions[candidate_id] = create_initial_state(candidate_id)
        
        state = self.sessions[candidate_id]
        
        #state: InterviewState = load_state(candidate_id)    
        
        if self._is_repeat_request(candidate_answer):
            return {
                "next_question": state.current_question,
                "interview_status": state.interview_status,
                "interview_round": state.interview_round
            }

    
        state.candidate_answer = candidate_answer
        state.confidence_score = confidence_score
        state.emotion_state = emotion_state

        #execute langgraph
        updated_state_dict = self.graph.invoke(state)
        updated_state = InterviewState(**updated_state_dict)


        # write to semantic memory
        if updated_state.knowledge_evaluation:
            self.memory.store_interaction(
                question=state.current_question,
                answer=candidate_answer,
                evaluation=updated_state.knowledge_evaluation,
                topic=(
                    updated_state.topics_covered[-1]
                    if updated_state.topics_covered
                    else "general"
                ),
                interview_round=updated_state.interview_round
            )

        #save it
        #read from memory and inject into state
        memory_summary = self.memory.summarize_candidate_profile()
        weak_topics = self.memory.get_weak_topics()
        
        updated_state.knowledge_evaluation["memory_summary"] = memory_summary
        updated_state.knowledge_evaluation["weak_topics"] = weak_topics

        #save updated state
        self.sessions[candidate_id] = updated_state
        

        return {
            "next_question": updated_state.next_question,
            "interview_status": updated_state.interview_status,
            "interview_round": updated_state.interview_round
        }


 # even if we did not write the : InterviewState, ig it would work, but for sustaining the InterviewState structure and its variables, we should put : InterviewState
        