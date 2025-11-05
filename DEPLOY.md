# LedgerTrace Deployment Guide

## Quick Deploy Options

### Option 1: GitHub Codespaces (Recommended)
1. Open this repository in GitHub Codespaces
2. Run: `docker-compose up --build`
3. Access via forwarded ports

### Option 2: Local Docker
```bash
git clone https://github.com/Adahandles/ledgertrace.git
cd ledgertrace
docker-compose up --build
```

### Option 3: Separate Services
```bash
# Backend only
cd backend
docker build -t ledgertrace-backend .
docker run -p 8000:8000 ledgertrace-backend

# Frontend only  
cd frontend
npm install
npm run build
npm run preview -- --host --port 5173
```

## Environment Configuration

### Backend (.env)
```env
# Optional - currently uses mock data
SUNBIZ_API_KEY=your_key_here
COUNTY_SCRAPER_DELAY=1.0
```

### Frontend (environment variables)
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Production Deployment

### Netlify/Vercel (Frontend Only)
1. Build static frontend: `npm run build`
2. Deploy `build/` directory
3. Set API base URL to your backend

### Railway/Render (Full Stack)
1. Connect GitHub repository
2. Deploy backend service first
3. Update frontend API URL
4. Deploy frontend service

## Port Configuration
- **Backend API:** 8000
- **Frontend:** 5173
- **Frontend Preview:** 4173

## Troubleshooting

### Common Issues
1. **Port conflicts:** Change ports in docker-compose.yml
2. **CORS errors:** Backend includes CORS middleware
3. **Build failures:** Check Node.js version (18+ required)

### Health Checks
```bash
# Backend health
curl http://localhost:8000/

# Frontend dev server
curl http://localhost:5173/
```