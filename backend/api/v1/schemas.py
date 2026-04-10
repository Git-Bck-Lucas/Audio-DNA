from pydantic import BaseModel
from datetime import datetime

class UserResponse(BaseModel):
    spotify_user_id: str
    created_at: datetime
    
    model_config = {"from_attributes": True}
    
class AnalysisResponse(BaseModel):
    user_id: int
    result: dict
    
    model_config = {"from_attributes": True}