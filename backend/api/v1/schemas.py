from pydantic import BaseModel
from datetime import datetime
from typing import Literal

Mode = Literal["science", "lucas"]

class UserResponse(BaseModel):
    spotify_user_id: str
    created_at: datetime
    
    model_config = {"from_attributes": True}
    
class AnalysisResponse(BaseModel):
    id: int
    user_id: int
    result: dict
    created_at: datetime
    
    model_config = {"from_attributes": True}
    
class TraitScore(BaseModel):
    score: float                                    # 0.0–1.0
    confidence: Literal["high", "medium", "low"]
    reasoning: str
    
class PersonalityScores(BaseModel):
    openness: TraitScore
    conscientiousness: TraitScore
    extraversion: TraitScore
    agreeableness: TraitScore
    neuroticism: TraitScore