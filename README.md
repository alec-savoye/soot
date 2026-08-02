# 🔥 Heat Map Website

A real-time heat map visualization system that displays location-based vibe scores (1-5) from clients. Built with Vue.js, FastAPI, PostgreSQL, and Docker.

## Features

- **Real-time Heat Map**: Visualizes vibe intensity with 10-mile radius heat layers
- **Token-based Authentication**: Secure client access via unique tokens
- **Browser GPS Integration**: Automatic geolocation with fallback to manual entry
- **Rate Limiting**: 5 submissions per minute per client token
- **Live Updates**: 30-second polling for real-time map updates
- **Admin Panel**: Generate and manage client tokens
- **Docker Deployment**: Bind-mounted data directories for persistence

## Tech Stack

- **Frontend**: Vue.js 3 + Leaflet.js (free alternative to Mapbox)
- **Backend**: Python FastAPI + SQLAlchemy
- **Database**: PostgreSQL (SQLite in production)
- **Containerization**: Docker + Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Node.js 20+ and npm (for local development)
- Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
cd soot
```

### 2. Start with Docker (Recommended)

```bash
# Create the data directory for bind mounts
mkdir -p backend/data

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### 3. Start with Local Development

```bash
# Backend (Python)
cd backend
python -m database.init_db
python -m uvicorn app:app --reload --port 8000

# In another terminal, Frontend (Node.js)
cd frontend
npm install
npm run dev
```

## Usage

### As an Administrator

1. Open `http://localhost:3000`
2. Click the "⚙️ Admin" button
3. Click "Generate New Token" to create a client token
4. Copy the generated token
5. Share the token with clients

### As a Client

1. Open `http://localhost:3000`
2. Click "🔐 Login"
3. Enter your token or use URL parameter: `http://localhost:3000?token=YOUR_TOKEN`
4. Allow browser geolocation when prompted
5. Enter your vibe score (1-5)
6. Your location appears on the heat map

### As a Visitor

1. Open `http://localhost:3000`
2. View the real-time heat map showing all submitted locations
3. See vibe intensity with color gradient (blue = low, red = high)
4. Click markers for details about each submission

## API Endpoints

### Authentication
- `POST /api/admin/generate` - Generate a new client token
- `DELETE /api/admin/delete` - Delete a token and its submissions

### Submissions
- `POST /api/submission` - Submit a location and vibe score
- `GET /api/submissions` - Get all submissions
- `GET /api/submissions/geojson` - Get submissions in GeoJSON format

### Health
- `GET /api/health` - Health check endpoint

## Configuration

### Docker Bind Mounts

The application uses bind mounts to persist data:

- `./backend/data:/var/lib/postgresql/data` - Database storage
- `./frontend/dist:/app/dist` - Frontend build output
- `./backend:/app` - Backend source code

### Rate Limiting

- **Limit**: 5 submissions per minute
- **Per Token**: Each client token has its own rate limit
- **Enforcement**: In-memory tracking (Redis recommended for production)

### Heat Map Settings

- **Radius**: 5000 meters (10 miles)
- **Blur**: 25 pixels
- **Color Gradient**: Blue → Cyan → Purple → Red (based on vibe score)

## Project Structure

```
soot/
├── frontend/                  # Vue.js frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue           # Main map view
│   │   ├── Admin.vue         # Admin panel
│   │   ├── api/
│   │   │   ├── client.js     # Client API calls
│   │   │   └── admin.js      # Admin API calls
│   │   └── style.css
│   └── package.json
├── backend/                   # FastAPI backend
│   ├── app.py                # Main application
│   ├── database/
│   │   ├── __init__.py       # Database setup
│   │   ├── schema.py         # SQLAlchemy models
│   │   └── init_db.py        # Database initialization
│   ├── routes/
│   │   └── clients.py        # API routes
│   ├── rate_limiter.py       # Rate limiting logic
│   ├── requirements.txt
│   └── data/                 # Bind mount for database
├── docker/
│   └── docker-compose.yml    # Docker orchestration
├── Dockerfile.frontend       # Frontend container
├── Dockerfile.backend        # Backend container
└── README.md
```

## Environment Variables

### Backend

```bash
DATABASE_URL=sqlite:///./data/heat_map.db  # For SQLite
```

For production with PostgreSQL:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/heat_map
```

## Troubleshooting

### Database Issues

If the database doesn't persist:
- Ensure `./backend/data` directory exists
- Check Docker permissions on the directory
- Verify bind mounts in docker-compose.yml

### Port Conflicts

If ports 3000 or 8000 are in use:
- Edit `docker-compose.yml` to use different ports
- Or stop running containers first: `docker-compose down`

### CORS Errors

If you see CORS errors:
- Ensure frontend is running on `http://localhost:3000`
- Backend CORS is configured for this origin

## Production Deployment

For production, consider:

1. **Database**: Switch to PostgreSQL with persistent volumes
2. **Rate Limiting**: Use Redis for distributed rate limiting
3. **Authentication**: Implement proper token expiration and revocation
4. **Security**: Add HTTPS, token validation, and input sanitization
5. **Monitoring**: Add logging and monitoring
6. **CDN**: Serve static assets from a CDN

## License

MIT License - Feel free to use and modify.
