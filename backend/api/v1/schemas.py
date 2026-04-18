from pydantic import BaseModel
from datetime import datetime

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