"""
LedgerTrace Security Configuration
Centralized security settings and environment management
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SecurityConfig:
    """Centralized security configuration management"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
        self.is_production = self.environment == "production"
        self.is_development = self.environment == "development"
        
    # API Security Settings
    @property
    def api_rate_limits(self) -> Dict[str, str]:
        """API rate limiting configuration"""
        if self.is_production:
            return {
                "analyze": "3/minute",        # Stricter in production
                "export": "2/minute",         # Resource intensive
                "ownership": "1/minute",      # Most intensive operation
                "health": "20/minute",
                "root": "5/minute",
                "download": "10/minute"
            }
        else:
            return {
                "analyze": "10/minute",       # More lenient for development
                "export": "5/minute",
                "ownership": "3/minute",
                "health": "60/minute",
                "root": "20/minute",
                "download": "30/minute"
            }
    
    @property
    def cors_origins(self) -> list:
        """CORS allowed origins based on environment"""
        if self.is_production:
            return [
                "https://ledgertrace.vercel.app",
                "https://ledgertrace.netlify.app", 
                "https://adahandles.github.io"
            ]
        else:
            return [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:3000",
                "http://localhost:8000"
            ]
    
    @property
    def trusted_hosts(self) -> list:
        """Trusted host configuration"""
        base_hosts = ["localhost", "127.0.0.1"]
        
        if self.is_production:
            return base_hosts + [
                "ledgertrace.vercel.app",
                "ledgertrace.netlify.app", 
                "adahandles.github.io"
            ]
        else:
            return base_hosts + ["*"]  # Allow all in development
    
    # Input Validation Limits
    @property
    def input_limits(self) -> Dict[str, int]:
        """Input validation limits"""
        return {
            "entity_name_max_length": 200,
            "address_max_length": 500,
            "officer_name_max_length": 200,
            "county_max_length": 50,
            "max_officers": 20,
            "max_export_sections": 10,
            "template_style_max_length": 50,
            "filename_max_length": 255,
            "max_ownership_depth": 10,
            "max_file_size_mb": 50
        }
    
    # File Security Settings
    @property
    def file_security(self) -> Dict[str, Any]:
        """File security configuration"""
        return {
            "allowed_extensions": [".pdf", ".json"],
            "export_directory_permissions": 0o750,
            "max_file_age_days": 30,  # Auto-cleanup old exports
            "scan_for_malware": self.is_production,
            "quarantine_suspicious_files": True
        }
    
    # External API Security
    @property
    def external_api_config(self) -> Dict[str, Any]:
        """External API security configuration"""
        return {
            "sunbiz_rate_limit_seconds": 3.0 if self.is_production else 2.0,
            "max_request_timeout_seconds": 15,
            "max_response_size_mb": 5,
            "enforce_ssl": True,
            "verify_certificates": True,
            "user_agent": "LedgerTrace/1.0 (+https://ledgertrace.com) Compliance Analysis Tool",
            "max_redirects": 3,
            "connection_pool_size": 10
        }
    
    # Logging and Monitoring
    @property
    def security_logging(self) -> Dict[str, Any]:
        """Security logging configuration"""
        return {
            "log_level": "INFO" if self.is_production else "DEBUG",
            "log_failed_requests": True,
            "log_rate_limit_violations": True,
            "log_input_validation_failures": True,
            "log_file_access": True,
            "log_suspicious_activity": True,
            "retention_days": 90
        }
    
    # Environment Variables
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Safely get secret from environment variables"""
        value = os.getenv(key, default)
        if value and key.upper() in ["PASSWORD", "SECRET", "TOKEN", "KEY"]:
            # Don't log secrets
            logger.debug(f"Retrieved secret for key: {key[:3]}***")
        return value
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate environment configuration"""
        issues = []
        warnings = []
        
        # Check required directories
        backend_dir = Path(__file__).parent.parent
        exports_dir = backend_dir / "exports"
        
        if not exports_dir.exists():
            warnings.append("Exports directory does not exist (will be created)")
        
        # Check permissions in production
        if self.is_production:
            if not os.getenv("SECRET_KEY"):
                issues.append("SECRET_KEY not set in production")
            
            if not self.cors_origins:
                issues.append("No CORS origins configured for production")
            
            if "localhost" in str(self.cors_origins):
                warnings.append("Localhost in CORS origins for production")
        
        # Check file system permissions
        try:
            test_file = exports_dir / ".security_test"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            issues.append(f"Cannot write to exports directory: {e}")
        
        return {
            "environment": self.environment,
            "is_secure": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "timestamp": "2024-12-19T10:00:00Z"
        }
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "X-Powered-By": "LedgerTrace Security Framework"
        }
        
        if self.is_production:
            headers.update({
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
                "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'"
            })
        
        return headers

# Global security configuration instance
security_config = SecurityConfig()

def get_security_config() -> SecurityConfig:
    """Get the global security configuration instance"""
    return security_config

def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
    """Log security-related events"""
    logger.warning(f"SECURITY EVENT: {event_type} | Details: {details}")

def validate_ip_address(ip: str) -> bool:
    """Validate IP address format"""
    import re
    
    # IPv4 pattern
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    # IPv6 pattern (simplified)
    ipv6_pattern = r'^[0-9a-fA-F:]+$'
    return bool(re.match(ipv6_pattern, ip)) and '::' in ip