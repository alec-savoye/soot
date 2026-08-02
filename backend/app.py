from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, timedelta
import os
import secrets

app = FastAPI(title="Heat Map API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
static_dir = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

# Import database setup
try:
    from database import init_db, SessionLocal, Base
    from database.schema import Submission
    from routes import clients
    app.include_router(clients.router, prefix="/api", tags=["clients"])
    
    @app.on_event("startup")
    async def startup():
        """Initialize database on startup"""
        try:
            init_db()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize database: {e}")
    
    # Add admin routes
    @app.post("/api/admin/generate")
    async def generate_token():
        """Generate a new random token for clients"""
        token = secrets.token_urlsafe(32)
        
        # Store token with timestamp (in memory for demo)
        from rate_limiter import rate_limits
        rate_limits[token] = []
        
        return {
            "success": True,
            "message": "Token generated successfully",
            "token": token
        }
    
    @app.delete("/api/admin/delete")
    async def delete_token(request: Request):
        """Delete a token and its submissions"""
        data = await request.json()
        token = data.get("token")
        
        if not token:
            return JSONResponse(status_code=400, content={"success": False, "message": "Token required"})
        
        db = SessionLocal()
        try:
            # Delete all submissions for this token
            db.query(Submission).filter(Submission.client_token == token).delete()
            db.commit()
            
            # Remove from rate limiter
            if token in rate_limits:
                del rate_limits[token]
            
            return {
                "success": True,
                "message": "Token and submissions deleted"
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()
    
except ImportError:
    print("Database not initialized yet. Run: python backend/init_db.py")

class SubmissionData(BaseModel):
    token: str = Field(..., description="Client authentication token")
    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")
    vibe_score: int = Field(..., ge=1, le=5, description="Vibe rating 1-5")
    
    @field_validator('token')
    @classmethod
    def validate_token(cls, v):
        if not v or len(v.strip()) < 4:
            raise ValueError('Token must be at least 4 characters')
        return v.strip()

class SubmissionResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    data: Optional[dict] = None

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/submission", response_model=SubmissionResponse)
async def create_submission(submission: SubmissionData):
    """
    Submit a location and vibe score.
    Rate limited to 5 submissions per minute per token.
    """
    try:
        db = SessionLocal()
        try:
            from rate_limiter import rate_limit_check
            
            if not rate_limit_check(submission.token, db):
                return SubmissionResponse(
                    success=False,
                    message="Rate limit exceeded: 5 submissions per minute"
                )
            
            new_submission = Submission(
                client_token=submission.token,
                latitude=submission.latitude,
                longitude=submission.longitude,
                vibe_score=submission.vibe_score
            )
            
            db.add(new_submission)
            db.commit()
            db.refresh(new_submission)
            
            response_token = submission.token
            
            return SubmissionResponse(
                success=True,
                message="Location submitted successfully",
                token=response_token,
                data={
                    "id": new_submission.id,
                    "latitude": new_submission.latitude,
                    "longitude": new_submission.longitude,
                    "vibe_score": new_submission.vibe_score,
                    "created_at": new_submission.created_at.isoformat()
                }
            )
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/submissions")
async def get_submissions():
    """Get all submissions for the map"""
    try:
        db = SessionLocal()
        try:
            submissions = db.query(Submission).order_by(Submission.created_at.desc()).all()
            
            return {
                "success": True,
                "count": len(submissions),
                "data": [{
                    "id": s.id,
                    "client_token": s.client_token,
                    "latitude": s.latitude,
                    "longitude": s.longitude,
                    "vibe_score": s.vibe_score,
                    "created_at": s.created_at.isoformat()
                } for s in submissions]
            }
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/submissions/geojson")
async def get_geojson():
    """Get submissions in GeoJSON format for Leaflet"""
    try:
        db = SessionLocal()
        try:
            submissions = db.query(Submission).all()
            
            return {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [s.longitude, s.latitude]
                    },
                    "properties": {
                        "vibe_score": s.vibe_score,
                        "created_at": s.created_at.isoformat()
                    }
                } for s in submissions]
            }
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/tokens")
async def get_all_tokens():
    """Get all unique tokens from database"""
    try:
        db = SessionLocal()
        try:
            tokens = db.query(Submission.client_token).distinct().all()
            token_list = [t.client_token for t in tokens]
            
            return {
                "success": True,
                "tokens": token_list,
                "count": len(token_list)
            }
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
