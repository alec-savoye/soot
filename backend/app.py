from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import secrets

app = FastAPI(title="Heat Map API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:5174", "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend is served by its own container (Vite dev server); backend is API-only.

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

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Note: /api/submission and /api/submissions are provided by routes/clients.py

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
