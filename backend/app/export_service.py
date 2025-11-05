"""
LedgerTrace Export Service
Handles PDF and JSON report generation with professional formatting
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

import weasyprint
from jinja2 import Environment, FileSystemLoader
from dateutil import tz

from .models import EntityInput, EntityReport, ExportRequest, ExportResponse
from .analyzer import analyze_entity


class ExportService:
    """Service for generating PDF and JSON reports from entity analysis"""
    
    def __init__(self):
        # Setup Jinja2 template environment with security settings
        template_dir = Path(__file__).parent / "templates"
        
        # Ensure template directory exists and is secure
        template_dir.mkdir(exist_ok=True)
        
        # Configure Jinja2 with security settings
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,  # Enable auto-escaping for security
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Create exports directory with secure permissions
        self.export_dir = Path(__file__).parent.parent / "exports"
        self.export_dir.mkdir(mode=0o750, exist_ok=True)  # Restricted permissions
        
        # Security: Validate export directory is within expected bounds
        self._validate_export_directory()
    
    def generate_report(self, export_request: ExportRequest) -> ExportResponse:
        """
        Generate PDF or JSON report based on export request
        
        Args:
            export_request: Request containing entity data and export preferences
            
        Returns:
            ExportResponse with file details and download information
        """
        try:
            # Analyze the entity
            entity_report = analyze_entity(export_request.entity_input)
            
            # Generate timestamp
            timestamp = datetime.now(tz.UTC).strftime("%Y-%m-%d_%H-%M-%S")
            
            # Create safe filename
            safe_name = self._sanitize_filename(entity_report.name)
            
            if export_request.export_format == "json":
                return self._generate_json_report(entity_report, export_request, safe_name, timestamp)
            else:  # PDF
                return self._generate_pdf_report(entity_report, export_request, safe_name, timestamp)
                
        except Exception as e:
            return ExportResponse(
                success=False,
                file_name="",
                export_format=export_request.export_format,
                generated_at=datetime.now(tz.UTC).isoformat(),
                entity_name=export_request.entity_input.name,
                error_message=f"Export failed: {str(e)}"
            )
    
    def _generate_json_report(
        self, 
        entity_report: EntityReport, 
        export_request: ExportRequest,
        safe_name: str,
        timestamp: str
    ) -> ExportResponse:
        """Generate JSON format report"""
        
        # Create comprehensive JSON structure
        json_data = {
            "report_metadata": {
                "entity_name": entity_report.name,
                "generated_at": datetime.now(tz.UTC).isoformat(),
                "analysis_timestamp": timestamp,
                "report_version": "1.0",
                "export_format": "json",
                "sections_included": export_request.include_sections
            },
            "entity_input": {
                "name": export_request.entity_input.name,
                "address": export_request.entity_input.address,
                "ein": export_request.entity_input.ein,
                "officers": export_request.entity_input.officers,
                "county": export_request.entity_input.county
            },
            "risk_assessment": {
                "overall_risk_score": entity_report.risk_score,
                "risk_level": self._get_risk_level(entity_report.risk_score),
                "anomaly_count": len(entity_report.anomalies),
                "anomalies": entity_report.anomalies
            },
            "analysis_results": {}
        }
        
        # Add analysis sections based on included sections
        if "entity_info" in export_request.include_sections:
            json_data["analysis_results"]["entity_classification"] = {
                "is_trust": entity_report.entity_type.is_trust,
                "trust_types": entity_report.entity_type.trust_types,
                "match_terms": entity_report.entity_type.match_terms,
                "risk_indicators": entity_report.entity_type.risk_indicators,
                "requires_regulation": entity_report.entity_type.requires_regulation,
                "high_risk": entity_report.entity_type.high_risk
            }
        
        if "county_offices" in export_request.include_sections and entity_report.property:
            json_data["analysis_results"]["property_analysis"] = {
                "county": entity_report.property.county,
                "address": entity_report.property.address,
                "parcel_id": entity_report.property.parcel_id,
                "owner_name": entity_report.property.owner_name,
                "land_use": entity_report.property.land_use,
                "market_value": entity_report.property.market_value,
                "delinquent_taxes": entity_report.property.delinquent_taxes,
                "source_url": entity_report.property.source_url,
                "county_offices": entity_report.property.offices,
                "verification_links": entity_report.property.verification_links
            }
        
        if "court_activity" in export_request.include_sections and entity_report.court_data:
            json_data["analysis_results"]["court_analysis"] = {
                "case_count": entity_report.court_data.case_count,
                "has_foreclosure": entity_report.court_data.has_foreclosure,
                "has_tax_lien": entity_report.court_data.has_tax_lien,
                "has_civil": entity_report.court_data.has_civil,
                "has_bankruptcy": entity_report.court_data.has_bankruptcy,
                "risk_indicators": entity_report.court_data.risk_indicators,
                "cases": [
                    {
                        "case_type": case.case_type,
                        "case_number": case.case_number,
                        "status": case.status,
                        "filed_date": case.filed_date,
                        "county": case.county,
                        "plaintiff": case.plaintiff,
                        "property_address": case.property_address,
                        "amount": case.amount,
                        "description": case.description,
                        "search_url": case.search_url
                    }
                    for case in entity_report.court_data.cases
                ]
            }
        
        if "domain_info" in export_request.include_sections and entity_report.domain_data:
            json_data["analysis_results"]["domain_analysis"] = {
                "domain_count": entity_report.domain_data.domain_count,
                "has_active_website": entity_report.domain_data.has_active_website,
                "risk_indicators": entity_report.domain_data.risk_indicators,
                "domains": [
                    {
                        "domain": domain.domain,
                        "registration_date": domain.registration_date,
                        "expiration_date": domain.expiration_date,
                        "registrar": domain.registrar,
                        "is_active": domain.is_active,
                        "whois_privacy": domain.whois_privacy
                    }
                    for domain in entity_report.domain_data.domains
                ]
            }
        
        if "grants_data" in export_request.include_sections and entity_report.grants_data:
            json_data["analysis_results"]["funding_analysis"] = {
                "total_awards": entity_report.grants_data.total_awards,
                "active_grants": entity_report.grants_data.active_grants,
                "active_contracts": entity_report.grants_data.active_contracts,
                "total_funding": entity_report.grants_data.total_funding,
                "problematic_awards": entity_report.grants_data.problematic_awards,
                "risk_indicators": entity_report.grants_data.risk_indicators,
                "has_federal_funding": entity_report.grants_data.has_federal_funding,
                "has_state_funding": entity_report.grants_data.has_state_funding,
                "has_compliance_issues": entity_report.grants_data.has_compliance_issues,
                "grants": [
                    {
                        "award_id": grant.award_id,
                        "title": grant.title,
                        "agency": grant.agency,
                        "award_date": grant.award_date,
                        "amount": grant.amount,
                        "type": grant.type,
                        "status": grant.status,
                        "period_start": grant.period_start,
                        "period_end": grant.period_end,
                        "description": grant.description,
                        "compliance_status": grant.compliance_status
                    }
                    for grant in entity_report.grants_data.grants
                ]
            }
        
        if "monitoring_data" in export_request.include_sections and entity_report.monitoring_data:
            json_data["analysis_results"]["monitoring_analysis"] = {
                "last_scan": entity_report.monitoring_data.last_scan,
                "scan_frequency": entity_report.monitoring_data.scan_frequency,
                "total_changes": entity_report.monitoring_data.total_changes,
                "high_risk_changes": entity_report.monitoring_data.high_risk_changes,
                "active_alert_count": entity_report.monitoring_data.active_alert_count,
                "monitoring_score": entity_report.monitoring_data.monitoring_score,
                "changes_detected": [
                    {
                        "type": change.type,
                        "description": change.description,
                        "date_detected": change.date_detected,
                        "risk_level": change.risk_level,
                        "data_source": change.data_source
                    }
                    for change in entity_report.monitoring_data.changes_detected
                ],
                "active_alerts": [
                    {
                        "alert_id": alert.alert_id,
                        "alert_type": alert.alert_type,
                        "severity": alert.severity,
                        "message": alert.message,
                        "created_at": alert.created_at,
                        "status": alert.status,
                        "related_changes": alert.related_changes
                    }
                    for alert in entity_report.monitoring_data.active_alerts
                ]
            }
        
        # Write JSON file
        filename = f"{safe_name}_report_{timestamp}.json"
        file_path = self.export_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        file_size = file_path.stat().st_size
        
        return ExportResponse(
            success=True,
            file_name=filename,
            export_format="json",
            file_size=file_size,
            generated_at=datetime.now(tz.UTC).isoformat(),
            entity_name=entity_report.name,
            risk_score=entity_report.risk_score,
            download_url=f"/exports/{filename}"
        )
    
    def _generate_pdf_report(
        self, 
        entity_report: EntityReport, 
        export_request: ExportRequest,
        safe_name: str,
        timestamp: str
    ) -> ExportResponse:
        """Generate PDF format report using HTML template"""
        
        # Prepare template context
        context = {
            "entity_name": entity_report.name,
            "entity_input": export_request.entity_input,
            "risk_score": entity_report.risk_score,
            "anomalies": entity_report.anomalies,
            "entity_type": entity_report.entity_type,
            "property": entity_report.property,
            "court_data": entity_report.court_data,
            "domain_data": entity_report.domain_data,
            "officer_data": entity_report.officer_data,
            "grants_data": entity_report.grants_data,
            "monitoring_data": entity_report.monitoring_data,
            "include_sections": export_request.include_sections,
            "generated_at": datetime.now(tz.UTC).strftime("%B %d, %Y at %H:%M UTC"),
            "analysis_date": datetime.now(tz.UTC).strftime("%Y-%m-%d"),
            "template_style": export_request.template_style or "professional"
        }
        
        # Render HTML template
        template = self.jinja_env.get_template("entity_report.html")
        html_content = template.render(**context)
        
        # Generate PDF
        filename = f"{safe_name}_report_{timestamp}.pdf"
        file_path = self.export_dir / filename
        
        # Create PDF with WeasyPrint
        html_doc = weasyprint.HTML(string=html_content)
        html_doc.write_pdf(str(file_path))
        
        file_size = file_path.stat().st_size
        
        return ExportResponse(
            success=True,
            file_name=filename,
            export_format="pdf",
            file_size=file_size,
            generated_at=datetime.now(tz.UTC).isoformat(),
            entity_name=entity_report.name,
            risk_score=entity_report.risk_score,
            download_url=f"/exports/{filename}"
        )
    
    def _sanitize_filename(self, name: str) -> str:
        """Create a safe filename from entity name with enhanced security"""
        if not name or not isinstance(name, str):
            return "entity_report"
        
        # Strip and validate input
        name = name.strip()
        if not name:
            return "entity_report"
        
        # Remove/replace unsafe characters - more restrictive for security
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        sanitized = "".join(c if c in safe_chars else "_" for c in name)
        
        # Remove path traversal attempts
        sanitized = sanitized.replace("..", "").replace("/", "_").replace("\\", "_")
        
        # Prevent special filenames
        reserved_names = {
            "con", "prn", "aux", "nul", "com1", "com2", "com3", "com4", 
            "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", 
            "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"
        }
        if sanitized.lower() in reserved_names:
            sanitized = f"entity_{sanitized}"
        
        # Limit length and clean up underscores
        sanitized = sanitized[:50].strip("_.")
        while "__" in sanitized:
            sanitized = sanitized.replace("__", "_")
        
        # Ensure filename is not empty and doesn't start with dot
        if not sanitized or sanitized.startswith("."):
            sanitized = f"entity_report_{sanitized}" if sanitized else "entity_report"
        
        return sanitized
    
    def _validate_export_directory(self) -> None:
        """Validate that export directory is secure and within bounds"""
        try:
            # Resolve to absolute path
            abs_export_dir = self.export_dir.resolve()
            
            # Check that directory is within the backend folder
            backend_dir = Path(__file__).parent.parent.resolve()
            if not str(abs_export_dir).startswith(str(backend_dir)):
                raise ValueError(f"Export directory outside of allowed path: {abs_export_dir}")
            
            # Ensure directory exists and has correct permissions
            if abs_export_dir.exists():
                # Check that it's actually a directory
                if not abs_export_dir.is_dir():
                    raise ValueError(f"Export path is not a directory: {abs_export_dir}")
                    
                # Update to secure permissions
                abs_export_dir.chmod(0o750)
            
        except Exception as e:
            raise RuntimeError(f"Export directory validation failed: {e}")
    
    def _validate_file_path(self, filename: str) -> Path:
        """Validate and return secure file path"""
        if not filename:
            raise ValueError("Filename cannot be empty")
        
        # Additional sanitization
        safe_filename = Path(filename).name  # Remove any path components
        
        # Check for path traversal
        if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
            raise ValueError(f"Invalid filename: {filename}")
        
        # Validate file extension
        allowed_extensions = {".pdf", ".json"}
        if not any(safe_filename.endswith(ext) for ext in allowed_extensions):
            raise ValueError(f"File extension not allowed: {safe_filename}")
        
        # Create full path
        file_path = self.export_dir / safe_filename
        
        # Ensure the resolved path is still within export directory
        try:
            resolved_path = file_path.resolve()
            if not str(resolved_path).startswith(str(self.export_dir.resolve())):
                raise ValueError(f"File path outside export directory: {resolved_path}")
        except Exception:
            raise ValueError(f"Invalid file path: {filename}")
        
        return file_path
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Convert risk score to descriptive level"""
        if risk_score < 30:
            return "Low Risk"
        elif risk_score < 70:
            return "Medium Risk"
        else:
            return "High Risk"
    
    def get_export_file_path(self, filename: str) -> Path:
        """Get the full path to an exported file with security validation"""
        return self._validate_file_path(filename)
    
    def list_exports(self) -> list:
        """List all available export files"""
        if not self.export_dir.exists():
            return []
        
        exports = []
        for file_path in self.export_dir.iterdir():
            if file_path.is_file() and file_path.suffix in ['.pdf', '.json']:
                exports.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                    "format": file_path.suffix[1:]  # Remove the dot
                })
        
        return sorted(exports, key=lambda x: x["created"], reverse=True)


# Global export service instance
export_service = ExportService()