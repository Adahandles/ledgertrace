from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import re
import html
import logging
from .analyzer import analyze_entity, analyze_ownership_chains
from .models import EntityInput, EntityReport, ExportRequest, ExportResponse, OwnershipAnalysisRequest, ShellCompanyReport
from .export_service import export_service
import os
import json

# Security logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

# Security headers middleware
class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    
                    # Add security headers
                    security_headers = [
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"DENY"),
                        (b"x-xss-protection", b"1; mode=block"),
                        (b"strict-transport-security", b"max-age=31536000; includeSubDomains"),
                        (b"content-security-policy", b"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"),
                        (b"referrer-policy", b"strict-origin-when-cross-origin"),
                        (b"permissions-policy", b"geolocation=(), microphone=(), camera=()"),
                    ]
                    
                    for header_name, header_value in security_headers:
                        headers[header_name] = header_value
                    
                    message["headers"] = list(headers.items())
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)

# Input sanitization functions
def sanitize_string(value: str, max_length: int = 500) -> str:
    """Sanitize string input to prevent XSS and other attacks."""
    if not value:
        return ""
    
    # HTML escape
    value = html.escape(value)
    
    # Remove control characters except newlines, tabs, and carriage returns
    value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
    
    # Limit length
    if len(value) > max_length:
        raise HTTPException(status_code=422, detail=f"Input too long (max {max_length} characters)")
    
    return value.strip()

def validate_ein(ein: str) -> bool:
    """Validate EIN format."""
    if not ein:
        return True  # EIN is optional
    
    # Remove hyphens and check if it's 9 digits
    clean_ein = ein.replace("-", "")
    if not re.match(r'^\d{9}$', clean_ein):
        return False
    
    return True

def validate_filename(filename: str) -> bool:
    """Validate filename to prevent path traversal attacks."""
    if not filename:
        return False
    
    # Check for path traversal attempts
    if ".." in filename or "/" in filename or "\\" in filename:
        return False
    
    # Check for valid characters (alphanumeric, hyphens, underscores, dots)
    if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        return False
    
    return True

# FastAPI app setup with security configurations
app = FastAPI(
    title="LedgerTrace API",
    description="AI-Powered Entity Risk Analysis for Financial Transparency",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    # Security configurations
    openapi_url="/api/openapi.json",  # Custom OpenAPI URL
    swagger_ui_oauth2_redirect_url=None,  # Disable OAuth redirect
    swagger_ui_init_oauth=None,  # Disable OAuth
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting
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
    expose_headers=["X-RateLimit-Remaining", "X-RateLimit-Limit", "Content-Disposition"]
)

@app.get("/")
@limiter.limit("10/minute")
def read_root(request: Request):
    """Root endpoint with rate limiting."""
    logger.info(f"Root endpoint accessed from {get_remote_address(request)}")
    return {
        "status": "LedgerTrace API is live",
        "version": "1.0.0",
        "docs": "/api/docs",
        "disclaimer": "All data sourced from public records. Not financial or legal advice.",
        "security": "Rate limited API with input validation"
    }

@app.get("/health")
@limiter.limit("30/minute")
def health_check(request: Request):
    """Health check endpoint with rate limiting."""
    return {"status": "healthy", "timestamp": "2025-11-05", "security": "protected"}

@app.post("/analyze", response_model=EntityReport)
@limiter.limit("5/minute")
def analyze(request: Request, input: EntityInput):
    """
    Analyze entity with comprehensive security validation
    - Rate limited to 5 requests per minute
    - Input sanitization and validation
    - Logging for security monitoring
    """
    client_ip = get_remote_address(request)
    logger.info(f"Analysis request from {client_ip} for entity: {input.name[:50]}...")
    
    try:
        # Enhanced input validation and sanitization
        sanitized_name = sanitize_string(input.name, 200)
        if not sanitized_name:
            raise HTTPException(status_code=422, detail="Entity name is required")
        
        # Sanitize address if provided
        sanitized_address = None
        if input.address:
            sanitized_address = sanitize_string(input.address, 500)
        
        # Validate EIN format
        if input.ein and not validate_ein(input.ein):
            raise HTTPException(status_code=422, detail="Invalid EIN format (must be XX-XXXXXXX or XXXXXXXXX)")
        
        # Sanitize officers list
        sanitized_officers = []
        if input.officers:
            if len(input.officers) > 20:
                raise HTTPException(status_code=422, detail="Too many officers listed (max 20)")
            
            for officer in input.officers:
                sanitized_officer = sanitize_string(officer, 200)
                if sanitized_officer:  # Only add non-empty names
                    sanitized_officers.append(sanitized_officer)
        
        # Sanitize county
        sanitized_county = None
        if input.county:
            sanitized_county = sanitize_string(input.county, 50)
        
        # Create sanitized input object
        sanitized_input = EntityInput(
            name=sanitized_name,
            address=sanitized_address,
            ein=input.ein,  # EIN already validated
            officers=sanitized_officers,
            county=sanitized_county
        )
        
        # Perform analysis
        result = analyze_entity(sanitized_input)
        logger.info(f"Analysis completed for {sanitized_name} from {client_ip}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed for {client_ip}: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")

@app.post("/export", response_model=ExportResponse)
@limiter.limit("3/minute")
def export_report(request: Request, export_request: ExportRequest):
    """
    Generate PDF or JSON report for an entity with enhanced security
    
    - Rate limited to 3 requests per minute
    - **entity_input**: Entity data to analyze and export
    - **export_format**: Choose "pdf" for formatted report or "json" for raw data
    - **include_sections**: Select which analysis sections to include
    - **template_style**: PDF template style (currently "professional")
    """
    client_ip = get_remote_address(request)
    logger.info(f"Export request from {client_ip} for entity: {export_request.entity_input.name[:50]}...")
    
    try:
        # Enhanced input validation and sanitization
        sanitized_name = sanitize_string(export_request.entity_input.name, 200)
        if not sanitized_name:
            raise HTTPException(status_code=422, detail="Entity name is required")
        
        # Validate export format
        if export_request.export_format not in ["pdf", "json"]:
            raise HTTPException(status_code=422, detail="Export format must be 'pdf' or 'json'")
        
        # Validate sections
        valid_sections = [
            "entity_info", "risk_score", "county_offices", "court_activity", 
            "domain_info", "grants_data", "monitoring_data", "ownership_data"
        ]
        invalid_sections = [s for s in export_request.include_sections if s not in valid_sections]
        if invalid_sections:
            raise HTTPException(
                status_code=422, 
                detail=f"Invalid sections: {invalid_sections}. Valid sections: {valid_sections}"
            )
        
        # Sanitize entity input
        sanitized_input = EntityInput(
            name=sanitized_name,
            address=sanitize_string(export_request.entity_input.address or "", 500) if export_request.entity_input.address else None,
            ein=export_request.entity_input.ein if validate_ein(export_request.entity_input.ein) else None,
            officers=[sanitize_string(officer, 200) for officer in (export_request.entity_input.officers or [])],
            county=sanitize_string(export_request.entity_input.county or "", 50) if export_request.entity_input.county else None
        )
        
        # Create sanitized export request
        sanitized_export_request = ExportRequest(
            entity_input=sanitized_input,
            export_format=export_request.export_format,
            include_sections=export_request.include_sections,
            template_style=sanitize_string(export_request.template_style or "professional", 50)
        )
    
        # Generate report
        export_response = export_service.generate_report(sanitized_export_request)
        
        if not export_response.success:
            logger.error(f"Export failed for {client_ip}: {export_response.error_message}")
            raise HTTPException(
                status_code=500, 
                detail=export_response.error_message or "Export generation failed"
            )
        
        logger.info(f"Export completed for {sanitized_name} from {client_ip}")
        return export_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export generation failed for {client_ip}: {str(e)}")
        raise HTTPException(status_code=500, detail="Export generation failed. Please try again.")@app.get("/exports/{filename}")
@limiter.limit("20/minute")
def download_export(request: Request, filename: str):
    """
    Download a generated export file with security validation
    
    - Rate limited to 20 downloads per minute
    - **filename**: Name of the file to download (from export response)
    """
    client_ip = get_remote_address(request)
    
    try:
        # Validate filename to prevent path traversal attacks
        if not validate_filename(filename):
            logger.warning(f"Invalid filename attempted from {client_ip}: {filename}")
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Additional security: only allow specific file extensions
        allowed_extensions = ['.pdf', '.json']
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            logger.warning(f"Unauthorized file extension attempted from {client_ip}: {filename}")
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        file_path = export_service.get_export_file_path(filename)
        
        if not file_path.exists():
            logger.warning(f"File not found request from {client_ip}: {filename}")
            raise HTTPException(status_code=404, detail="Export file not found")
        
        # Determine media type
        if filename.endswith('.pdf'):
            media_type = "application/pdf"
            headers = {"Content-Disposition": f"attachment; filename={filename}"}
        elif filename.endswith('.json'):
            media_type = "application/json"
            headers = {"Content-Disposition": f"attachment; filename={filename}"}
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            headers=headers,
            filename=filename
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="File download failed")

@app.get("/exports")
def list_exports(request: Request):
    """
    List all available export files
    
    Returns a list of export files with metadata
    """
    try:
        exports = export_service.list_exports()
        return {
            "exports": exports,
            "total_files": len(exports),
            "formats_available": list(set(exp["format"] for exp in exports))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list exports")

@app.post("/ownership-analysis", response_model=ShellCompanyReport)
@limiter.limit("2/minute")
async def analyze_ownership(request: Request, analysis_request: OwnershipAnalysisRequest):
    """
    Analyze ownership chains and detect shell company structures with enhanced security
    
    - Rate limited to 2 requests per minute (resource intensive operation)
    - **entity_name**: Name of entity to trace ownership for
    - **max_depth**: Maximum depth to search for ownership chains (1-10)
    - **include_inactive**: Include inactive entities in analysis
    - **similarity_threshold**: Officer name similarity threshold (0.5-1.0)
    
    Returns detailed ownership chain analysis with shell company risk assessment
    """
    client_ip = get_remote_address(request)
    logger.info(f"Ownership analysis request from {client_ip} for entity: {analysis_request.entity_name[:50]}...")
    
    try:
        # Enhanced input validation and sanitization
        sanitized_name = sanitize_string(analysis_request.entity_name, 200)
        if not sanitized_name:
            raise HTTPException(status_code=422, detail="Entity name is required")
        
        # Validate numeric parameters
        if analysis_request.max_depth < 1 or analysis_request.max_depth > 10:
            raise HTTPException(status_code=422, detail="Max depth must be between 1 and 10")
            
        if analysis_request.similarity_threshold < 0.5 or analysis_request.similarity_threshold > 1.0:
            raise HTTPException(status_code=422, detail="Similarity threshold must be between 0.5 and 1.0")
    
        # Run ownership analysis with sanitized input
        ownership_report = await analyze_ownership_chains(sanitized_name)
        
        if not ownership_report:
            # Return default report if no ownership chains found
            logger.info(f"No ownership chains found for {sanitized_name} from {client_ip}")
            return ShellCompanyReport(
                entity_name=sanitized_name,
                analysis_date="2024-12-19T10:00:00Z",
                risk_assessment="LOW",
                shell_company_probability=0.0,
                ownership_chains_found=0,
                deepest_chain_depth=0,
                total_shell_indicators=0,
                total_obfuscation_patterns=0,
                max_risk_score=0.0,
                avg_risk_score=0.0,
                ownership_chains=[],
                summary=f"No complex ownership structures detected for {sanitized_name}"
            )
        
        # Convert dict to model and return
        logger.info(f"Ownership analysis completed for {sanitized_name} from {client_ip}")
        return ShellCompanyReport(**ownership_report)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ownership analysis failed for {client_ip}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Ownership analysis failed. Please try again."
        )
