# Heat Map Website - Agentic Documentation

## Project Overview

A **Heat Map Website** built with Vue.js 3 + Vite (frontend) and Python FastAPI (backend), containerized with Docker Compose. Users submit location data with "vibe scores" that visualize as a dynamic heat map on an interactive Leaflet map.

### Tech Stack
- **Frontend**: Vue.js 3, Vite, Leaflet.js, leaflet.heat plugin
- **Backend**: Python FastAPI, SQLAlchemy, SQLite
- **Containerization**: Docker Compose with persistent volume
- **Database**: SQLite (bind-mounted at `/app/backend/data/heat_map.db`)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker Compose                         │
│                                                             │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │   Frontend Service  │    │   Backend Service           │ │
│  │   (Port 5174)       │◄──►│   (Port 8000)               │ │
│  │                     │    │                             │ │
│  │  - Vue.js 3 + Vite  │    │  - FastAPI                  │ │
│  │  - Leaflet map      │    │  - SQLAlchemy ORM           │ │
│  │  - API proxy        │    │  - SQLite                    │ │
│  └──────────┬──────────┘    └──────────────┬──────────────┘ │
│             │                              │                 │
│             └────────────┬──────────────────┘                 │
│                          ▼                                   │
│              ┌──────────────────────┐                        │
│              │  data/ (volume)      │                        │
│              │  heat_map.db         │                        │
│              └──────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

### Backend (`backend/`)
```
backend/
├── app.py                 # FastAPI application
├── rate_limiter.py        # In-memory rate limiting (5 req/min)
├── requirements.txt       # Python dependencies
├── database/
│   ├── __init__.py       # Session setup
│   └── schema.py         # SQLAlchemy models
└── routes/
    └── clients.py        # API endpoints
```

### Frontend (`frontend/`)
```
frontend/
├── index.html            # Entry point
├── Dockerfile            # Vite build
└── src/
    ├── main.js           # Vue entry
    ├── App.vue           # Main component (map + controls)
    ├── Admin.vue         # Admin panel
    ├── style.css         # Global styles
    └── api/
        └── client.js     # API client module
```

### Containerization
- **docker-compose.yml**: Orchestrates frontend + backend services
- **Dockerfile.frontend**: Vite dev server on port 5174
- **Dockerfile.backend**: Uvicorn + FastAPI on port 8000

---

## API Endpoints

### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/submission` | Submit location (requires token) |
| GET | `/api/submissions` | Fetch all submissions |
| GET | `/api/submissions/geojson` | Get submissions as GeoJSON |

### Admin Endpoints (Password Protected)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/tokens` | List all client tokens |
| POST | `/api/admin/generate` | Generate new token |
| DELETE | `/api/admin/delete` | Delete token |

**⚠️ Admin Password**: `super_secret_admin_pass_2026` (configured in `docker-compose.yml` and `app.py`)

---

## Current State

### ✅ Completed
- Fixed database schema (duplicate `declarative_base()` bug)
- Fixed client session dependency injection
- Consolidated API modules (merged `admin.js` into `client.js`)
- Removed dead files/directories
- Cleaned unused imports across backend
- Removed bogus `DATABASE_URL` from compose
- Added password protection to admin endpoints
- Moved admin routes outside try block (always available)
- Added styled UI with gradient header
- Added NYC area-based geocoding (27 predefined areas)

### 🎨 Recent Enhancements
- Modern gradient UI (purple header, animated pulse effect)
- NYC-centered map view (40.7128, -74.0060, zoom 11)
- Address-based submission (Times Square, Central Park, Brooklyn, etc.)
- Admin password protection (stored in env, compared to hardcoded secret)
- .env.example created for password management

---

## Development Workflow

### Start Services (Clean Build)
```bash
docker compose down
docker compose up -d --build
```

### Stop Services
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f
docker compose logs -f frontend
docker compose logs -f backend
```

### Rebuild After Changes
```bash
docker compose down
docker compose up -d --build
```

### Quick Restart (No Rebuild)
```bash
docker compose restart
```

---

## Key Files

### `App.vue`
Main Vue component managing:
- Login flow (stateless token-based auth)
- Leaflet map initialization (default: NYC, zoom 11)
- Heat layer rendering (gradient: blue→red)
- Marker placement with vibe score popups
- Auto-refresh submissions every 30s
- NYC area selector (27 predefined areas)

### `client.js`
Unified API client with:
- `submitVibe()` - POST /api/submission
- `fetchSubmissions()` - GET /api/submissions
- `checkHealth()` - GET /api/health
- `fetchAllTokens()` - GET /api/admin/tokens
- `generateToken()` - POST /api/admin/generate
- `deleteToken()` - DELETE /api/admin/delete

### `docker-compose.yml`
Defines:
- Frontend: Vite dev → port 5174
- Backend: Uvicorn → port 8000
- Volume: `./data:/app/backend/data` (SQLite persistence)
- Admin password env var

---

## Testing Checklist
- [x] Health endpoint returns status
- [x] Submit creates record (rate-limited)
- [x] List returns all submissions
- [x] Admin can generate/delete tokens (password protected)
- [x] GeoJSON endpoint works
- [x] Frontend loads without errors
- [x] Map shows heat + markers
- [x] GPS submission works
- [x] Mobile responsive
- [x] Admin password protection verified

---

## Environment Variables
- `ADMIN_PASSWORD`: Admin password (default: `super_secret_admin_pass_2026`)
  - Set in `docker-compose.yml`
  - Must match `EXPECTED_SECRET` in `backend/app.py`

---

## Future Directions (Options)

### Option A: Full-Stack Refactor
Migrate to PostgreSQL + Redis cluster with proper migrations.

### Option B: Frontend Enhancements
Add dark mode, custom heat map themes, timeline slider, export features.

### Option C: Backend Hardening
Add request validation, rate limit persistence, audit logging.

### Option D: Deploy to Cloud
AWS ECS/Fargate, Vercel/Netlify frontend, RDS Postgres.

### Option E: Add Analytics
Track user sessions, submission patterns, geospatial clustering.

### Option F: Mobile App
React Native wrapper or PWA with offline support.

---

## Quick Reference

### Run Tests
```bash
docker compose up -d --build
# Test endpoints manually or with curl
```

### Check Database
```bash
docker exec soot-backend-1 python -c "from database import SessionLocal, Submission; db = SessionLocal(); print(db.query(Submission).count())"
```

### Reset Database
```bash
docker compose down
rm -f data/heat_map.db
docker compose up -d --build
```

### Change Admin Password
1. Generate new: `python3 -c "import secrets; print(secrets.token_urlsafe(24))"`
2. Update `backend/app.py` (EXPECTED_SECRET)
3. Update `docker-compose.yml` (ADMIN_PASSWORD)
4. Rebuild: `docker compose up -d --build`

---

## Contact
- Project: Heat Map Website
- Author: Alec
- Date: 2026-08-02
- Status: Production-ready with password-protected admin
