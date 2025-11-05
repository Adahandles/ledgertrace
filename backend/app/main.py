from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .analyzer import analyze_entity
from .models import EntityInput, EntityReport
import os

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="LedgerTrace API",
    description="AI-Powered Entity Risk Analysis for Financial Transparency",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Security middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Trusted host middleware (production domains)
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "ledgertrace.vercel.app", 
    "ledgertrace.netlify.app",
    "adahandles.github.io"
]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)

# CORS middleware with strict origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://ledgertrace.vercel.app",
    "https://ledgertrace.netlify.app", 
    "https://adahandles.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,  # More secure for public API
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-RateLimit-Remaining", "X-RateLimit-Limit"]
)

@app.get("/")
@limiter.limit("10/minute")
def read_root(request: Request):
    return {
        "status": "LedgerTrace API is live",
        "version": "1.0.0",
        "docs": "/api/docs",
        "disclaimer": "All data sourced from public records. Not financial or legal advice."
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2025-11-05"}

@app.post("/analyze", response_model=EntityReport)
@limiter.limit("20/minute")  # Rate limit analysis requests
def analyze(request: Request, input: EntityInput):
    # Input validation
    if len(input.name) > 200:
        raise HTTPException(status_code=422, detail="Entity name too long (max 200 characters)")
    
    if input.address and len(input.address) > 500:
        raise HTTPException(status_code=422, detail="Address too long (max 500 characters)")
    
    if input.officers and len(input.officers) > 20:
        raise HTTPException(status_code=422, detail="Too many officers listed (max 20)")
    
    # Validate EIN format if provided
    if input.ein and not input.ein.replace("-", "").isdigit():
        raise HTTPException(status_code=422, detail="Invalid EIN format")
    
    try:
        result = analyze_entity(input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")
