from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
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

# Admin password protection
EXPECTED_SECRET = "super_secret_admin_pass_2026"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Import database setup
try:
    from database import init_db, SessionLocal, Base
    from database.schema import Submission
    from routes import clients
    app.include_router(clients.router, prefix="/api", tags=["clients"])
    
    @app.on_event("startup")
    async def startup():
        try:
            init_db()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize database: {e}")
    
except ImportError:
    print("Database not initialized yet. Run: python backend/init_db.py")

# Admin routes
@app.post("/api/admin/generate")
async def generate_token():
    if not ADMIN_PASSWORD or ADMIN_PASSWORD != EXPECTED_SECRET:
        return JSONResponse(status_code=401, content={"success": False, "message": "Access denied"})
    
    token = secrets.token_urlsafe(32)
    from rate_limiter import rate_limits
    rate_limits[token] = []
    
    return {"success": True, "message": "Token generated successfully", "token": token}

@app.delete("/api/admin/delete")
async def delete_token(request: Request):
    if not ADMIN_PASSWORD or ADMIN_PASSWORD != EXPECTED_SECRET:
        return JSONResponse(status_code=401, content={"success": False, "message": "Access denied"})
    
    data = await request.json()
    token = data.get("token")
    
    if not token:
        return JSONResponse(status_code=400, content={"success": False, "message": "Token required"})
    
    db = SessionLocal()
    try:
        db.query(Submission).filter(Submission.client_token == token).delete()
        db.commit()
        if token in rate_limits:
            del rate_limits[token]
        return {"success": True, "message": "Token and submissions deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/admin/tokens")
async def get_all_tokens():
    if not ADMIN_PASSWORD or ADMIN_PASSWORD != EXPECTED_SECRET:
        return JSONResponse(status_code=401, content={"success": False, "message": "Access denied"})
    
    try:
        db = SessionLocal()
        try:
            tokens = db.query(Submission.client_token).distinct().all()
            return {"success": True, "tokens": [t.client_token for t in tokens], "count": len(tokens)}
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/submissions/geojson")
async def get_geojson():
    try:
        db = SessionLocal()
        try:
            submissions = db.query(Submission).all()
            return {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [s.longitude, s.latitude]},
                    "properties": {"vibe_score": s.vibe_score, "created_at": s.created_at.isoformat()}
                } for s in submissions]
            }
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
