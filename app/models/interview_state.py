#interview_state.py
from enum import Enum
from typing import List, Optional , Any , Dict
from pydantic import BaseModel, Field

class InterviewStatus(str, Enum):
    ONGOING = "ongoing"
    ENDED = "ended"

class DecisionType(str, Enum):
    ASK_FOLLOWUP = "ASK_FOLLOWUP"
    NEXT_TOPIC = "NEXT_TOPIC"
    INCREASE_DIFFICULTY = "INCREASE_DIFFICULTY"
    END_INTERVIEW = "END_INTERVIEW"

class InterviewState(BaseModel):

    candidate_id : str
    interview_status: InterviewStatus = InterviewStatus.ONGOING
    interview_round: int = 1
    max_rounds: int = 5

    current_question: Optional[str] = None
    candidate_answer: Optional[str] = None
    past_questions: List[str] = Field(default_factory=list)

    knowledge_evaluation: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = 0.5
    emotion_state: str = "calm"

    topics_covered: List[str] = Field(default_factory=list)

    decision: Optional[DecisionType] = None
    next_question : Optional[str] = None

    class Config:
        validate_assignment = True
        use_enum_values = True


def create_initial_state(
        candidate_id: str,
        max_rounds: int = 5
) -> InterviewState:
    
    return InterviewState(
        candidate_id = candidate_id,
        max_rounds=max_rounds
    )

