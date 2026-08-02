import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()

# In-memory rate limiter (for demo - replaces Redis)
# Structure: { token: [timestamp1, timestamp2, ...] }
rate_limits: Dict[str, List[datetime]] = {}
rate_limit_window = 60  # seconds
rate_limit_max = 5  # submissions per minute

def rate_limit_check(token: str, db: Session) -> bool:
    """
    Check if client has exceeded rate limit.
    Returns True if allowed, False if rate limited.
    """
    current_time = datetime.utcnow()
    window_start = current_time.timestamp() - rate_limit_window
    
    # Get or create list of timestamps for this token
    if token not in rate_limits:
        rate_limits[token] = []
    
    # Clean old entries and count recent ones
    recent_submissions = [
        ts for ts in rate_limits[token]
        if ts.timestamp() >= window_start
    ]
    
    if len(recent_submissions) >= rate_limit_max:
        return False
    
    # Add this submission
    rate_limits[token].append(current_time)
    
    return True

def get_all_tokens(db: Session):
    """Get all unique tokens from database"""
    tokens = db.query(Submission.client_token).distinct().all()
    return [t.client_token for t in tokens]

class Submission(BaseModel):
    id: int
    client_token: str
    latitude: float
    longitude: float
    vibe_score: int
    created_at: datetime
    
    class Config:
        from_attributes = True
