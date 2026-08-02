from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List
from datetime import datetime

router = APIRouter()

from database import SessionLocal, Submission

class SubmissionRequest(BaseModel):
    token: str
    latitude: float
    longitude: float
    vibe_score: int

class SubmissionResponse(BaseModel):
    success: bool
    message: str
    token: str
    data: dict

class SubmissionsResponse(BaseModel):
    success: bool
    count: int
    data: List[Submission]

@router.post("/submission")
async def create_submission(request: SubmissionRequest, db: Session = Depends(SessionLocal)):
    """
    Submit a location and vibe score.
    Rate limited to 5 submissions per minute per token.
    """
    # Check rate limit
    from rate_limiter import rate_limit_check
    
    if not rate_limit_check(request.token, db):
        return SubmissionResponse(
            success=False,
            message="Rate limit exceeded: 5 submissions per minute"
        )
    
    # Create submission
    new_submission = Submission(
        client_token=request.token,
        latitude=request.latitude,
        longitude=request.longitude,
        vibe_score=request.vibe_score
    )
    
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    
    return SubmissionResponse(
        success=True,
        message="Location submitted successfully",
        token=request.token,
        data={
            "id": new_submission.id,
            "latitude": new_submission.latitude,
            "longitude": new_submission.longitude,
            "vibe_score": new_submission.vibe_score,
            "created_at": new_submission.created_at.isoformat()
        }
    )

@router.get("/submissions")
async def get_submissions(db: Session = Depends(SessionLocal)):
    """Get all submissions for the map"""
    submissions = db.query(Submission).order_by(Submission.created_at.desc()).all()
    
    return SubmissionsResponse(
        success=True,
        count=len(submissions),
        data=[{
            "id": s.id,
            "client_token": s.client_token,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "vibe_score": s.vibe_score,
            "created_at": s.created_at.isoformat()
        } for s in submissions]
    )

@router.get("/tokens")
async def get_all_tokens(db: Session = Depends(SessionLocal)):
    """Admin endpoint to get all tokens"""
    tokens = db.query(Submission.client_token).distinct().all()
    token_list = [t.client_token for t in tokens]
    
    return {
        "success": True,
        "tokens": token_list,
        "count": len(token_list)
    }
