from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.db.repository import get_user_by_id
from backend.db.models import User

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return user