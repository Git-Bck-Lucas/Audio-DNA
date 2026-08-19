from fastapi import HTTPException, Depends
from backend.api.dependencies import get_current_user
from backend.db.models import User
import time

WINDOW_SECONDS = 3600
MAX_REQUESTS = 5

# user_id -> (window_start_timestamp, count)
_hits: dict[int, tuple[float, int]] = {}

async def rate_limit_analysis(user: User = Depends(get_current_user)) -> User:
    now = time.time()
    user_id = user.id
    
    entry = _hits.get(user_id)
    if entry is None or now - entry[0] > WINDOW_SECONDS:
        _hits[user_id] = (now, 1)
        return user
    
    window_start, count = entry
    
    if count < MAX_REQUESTS:
        _hits[user_id] = (window_start, count + 1)
        return user
    
    retry_after = int(window_start + WINDOW_SECONDS - now)
    raise HTTPException(
        status_code=429,
        detail="Rate limit exceeded",
        headers={"Retry-After": str(retry_after)},
    )
    