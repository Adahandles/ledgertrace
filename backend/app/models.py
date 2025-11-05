from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
import re
import html

class EntityInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Entity name to analyze")
    address: Optional[str] = Field(None, max_length=500, description="Entity address for property analysis")
    ein: Optional[str] = Field(None, max_length=12, pattern=r"^\d{2}-?\d{7}$", description="Federal EIN number")
    officers: Optional[List[str]] = Field(default_factory=list, max_length=20, description="List of officers")
    county: Optional[str] = Field(None, max_length=50, description="Florida county name")
    
    @validator('name', 'address', 'county', pre=True)
    def sanitize_text_fields(cls, v):
        """Sanitize text input to prevent XSS and injection attacks."""
        if v is None:
            return v
        if isinstance(v, str):
            # HTML escape
            v = html.escape(v.strip())
            # Remove control characters except normal whitespace
            v = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', v)
            return v
        return v
    
    @validator('officers', pre=True)
    def sanitize_officers_list(cls, v):
        """Sanitize officers list."""
        if v is None:
            return []
        if isinstance(v, list):
            sanitized = []
            for officer in v:
                if isinstance(officer, str):
                    sanitized_officer = html.escape(officer.strip())
                    sanitized_officer = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized_officer)
                    if sanitized_officer:  # Only add non-empty names
                        sanitized.append(sanitized_officer)
            return sanitized
        return []
    
    @validator('ein', pre=True)
    def validate_ein_format(cls, v):
        """Validate EIN format with additional security checks."""
        if v is None:
            return v
        if isinstance(v, str):
            # Remove any non-digit/hyphen characters
            clean_ein = re.sub(r'[^\d-]', '', v)
            # Check format
            if clean_ein and re.match(r'^\d{2}-?\d{7}$', clean_ein):
                return clean_ein
            elif clean_ein == "":
                return None
            else:
                raise ValueError("Invalid EIN format")
        return v

class PropertyData(BaseModel):
    county: str
    address: str
    parcel_id: Optional[str] = Field(None, description="Property parcel identification number")
    owner_name: str
    land_use: str
    market_value: str
    delinquent_taxes: bool
    source_url: str
    offices: Optional[Dict[str, Any]] = Field(default_factory=dict, description="County office information as dictionaries")
    verification_links: Optional[Dict[str, str]] = Field(default_factory=dict, description="Direct verification links for this property")

class CourtCase(BaseModel):
    case_type: str = Field(..., description="Type of court case (Foreclosure, Tax Lien, etc.)")
    case_number: Optional[str] = Field(None, description="Court case number")
    status: str = Field(..., description="Case status (Open, Closed, Judgment, etc.)")
    filed_date: Optional[str] = Field(None, description="Date case was filed")
    county: Optional[str] = Field(None, description="County where case was filed")
    plaintiff: Optional[str] = Field(None, description="Plaintiff in the case")
    property_address: Optional[str] = Field(None, description="Property address if applicable")
    amount: Optional[str] = Field(None, description="Dollar amount involved")
    description: Optional[str] = Field(None, description="Case description")
    search_url: Optional[str] = Field(None, description="URL to search court records")

class CourtData(BaseModel):
    cases: List[CourtCase] = Field(default_factory=list, description="List of court cases involving entity")
    risk_indicators: List[str] = Field(default_factory=list, description="Court-related risk indicators") 
    case_count: int = Field(0, description="Total number of cases found")
    has_foreclosure: bool = Field(False, description="Entity involved in foreclosure cases")
    has_tax_lien: bool = Field(False, description="Entity has tax lien cases")
    has_civil: bool = Field(False, description="Entity involved in civil litigation")
    has_bankruptcy: bool = Field(False, description="Entity involved in bankruptcy")

class EntityType(BaseModel):
    is_trust: bool = Field(False, description="Whether entity is classified as a trust")
    trust_types: List[str] = Field(default_factory=list, description="Specific trust type classifications")
    match_terms: List[str] = Field(default_factory=list, description="Keywords that triggered classification")
    risk_indicators: List[str] = Field(default_factory=list, description="Risk indicators found in entity structure")
    requires_regulation: bool = Field(False, description="Whether trust type requires regulatory filing")
    high_risk: bool = Field(False, description="Whether trust is classified as high-risk type")

class DomainInfo(BaseModel):
    domain: str = Field(..., description="Domain name")
    whois: Dict[str, Any] = Field(default_factory=dict, description="WHOIS data for domain")
    website: Dict[str, Any] = Field(default_factory=dict, description="Website status and content info")
    match_confidence: float = Field(0.0, description="Confidence that domain belongs to entity")

class DomainData(BaseModel):
    domains: List[DomainInfo] = Field(default_factory=list, description="List of domains associated with entity")
    domain_count: int = Field(0, description="Number of domains found")
    risk_indicators: List[str] = Field(default_factory=list, description="Domain-related risk indicators")
    has_active_website: bool = Field(False, description="Entity has active website")
    has_privacy_protection: bool = Field(False, description="Uses privacy protection on domains")
    recent_registration: bool = Field(False, description="Recently registered domains")

class OfficerInfo(BaseModel):
    name: str = Field(..., description="Officer name")
    matched_name: str = Field(..., description="Matched name in database")
    confidence: float = Field(0.0, description="Confidence in name match")
    total_entities: int = Field(0, description="Total entities officer is connected to")
    active_entities: int = Field(0, description="Currently active entities")
    connected_entities: List[str] = Field(default_factory=list, description="Other entities officer is involved with")
    addresses: List[str] = Field(default_factory=list, description="Known addresses for officer")
    business_affiliations: List[str] = Field(default_factory=list, description="Professional licenses and affiliations")
    risk_flags: List[str] = Field(default_factory=list, description="Risk indicators for this officer")

class CrossReference(BaseModel):
    type: str = Field(..., description="Type of cross-reference (shared_entity, shared_address)")
    entity_name: Optional[str] = Field(None, description="Shared entity name")
    address: Optional[str] = Field(None, description="Shared address")
    officers: List[str] = Field(default_factory=list, description="Officers involved in cross-reference")
    risk_level: str = Field("low", description="Risk level of cross-reference")

class OfficerData(BaseModel):
    officers: List[OfficerInfo] = Field(default_factory=list, description="Officer analysis results")
    cross_references: List[CrossReference] = Field(default_factory=list, description="Cross-reference analysis")
    risk_indicators: List[str] = Field(default_factory=list, description="Officer-related risk indicators")
    total_entities_connected: int = Field(0, description="Total entities connected through officers")
    has_shared_officers: bool = Field(False, description="Officers shared with other entities")
    has_problematic_officers: bool = Field(False, description="Officers with risk indicators")

class GrantAward(BaseModel):
    award_id: str = Field(..., description="Grant or contract award ID")
    title: str = Field(..., description="Award title")
    agency: str = Field(..., description="Awarding agency")
    award_date: str = Field(..., description="Date award was made")
    amount: str = Field(..., description="Award amount")
    type: str = Field(..., description="Award type (Grant, Contract, etc.)")
    status: str = Field(..., description="Current award status")
    period_start: str = Field(..., description="Award period start date")
    period_end: str = Field(..., description="Award period end date")
    description: str = Field(..., description="Award description")
    compliance_status: str = Field(..., description="Compliance status")

class GrantsData(BaseModel):
    grants: List[GrantAward] = Field(default_factory=list, description="Grant awards")
    contracts: List[GrantAward] = Field(default_factory=list, description="Contract awards")
    total_awards: int = Field(0, description="Total number of awards")
    active_grants: int = Field(0, description="Number of active grants")
    active_contracts: int = Field(0, description="Number of active contracts")
    total_funding: float = Field(0.0, description="Total funding amount")
    problematic_awards: int = Field(0, description="Awards with compliance issues")
    risk_indicators: List[str] = Field(default_factory=list, description="Grant-related risk indicators")
    has_federal_funding: bool = Field(False, description="Received federal funding")
    has_state_funding: bool = Field(False, description="Received state funding")
    has_compliance_issues: bool = Field(False, description="Has compliance violations")

class Change(BaseModel):
    type: str = Field(..., description="Type of change detected")
    description: str = Field(..., description="Description of the change")
    date_detected: str = Field(..., description="When the change was detected")
    risk_level: str = Field("low", description="Risk level of change")
    data_source: str = Field(..., description="Source where change was detected")

class Alert(BaseModel):
    alert_id: str = Field(..., description="Unique alert identifier")
    alert_type: str = Field(..., description="Type of alert")
    severity: str = Field(..., description="Alert severity level")
    message: str = Field(..., description="Alert message")
    created_at: str = Field(..., description="When alert was created")
    status: str = Field("active", description="Alert status")
    related_changes: List[str] = Field(default_factory=list, description="Related change IDs")

class TrendAnalysis(BaseModel):
    metric: str = Field(..., description="Metric being analyzed")
    trend: str = Field(..., description="Trend direction (increasing, decreasing, stable)")
    confidence: float = Field(0.0, description="Confidence in trend analysis")
    time_period: str = Field(..., description="Time period analyzed")
    data_points: int = Field(0, description="Number of data points used")
    significance: str = Field("low", description="Statistical significance of trend")

class MonitoringData(BaseModel):
    changes_detected: List[Change] = Field(default_factory=list, description="Recent changes detected")
    active_alerts: List[Alert] = Field(default_factory=list, description="Active monitoring alerts")
    trends: List[TrendAnalysis] = Field(default_factory=list, description="Trend analysis results")
    last_scan: str = Field(..., description="Last monitoring scan timestamp")
    scan_frequency: str = Field("daily", description="Monitoring scan frequency")
    total_changes: int = Field(0, description="Total changes detected")
    high_risk_changes: int = Field(0, description="High risk changes detected")
    active_alert_count: int = Field(0, description="Number of active alerts")
    monitoring_score: int = Field(0, description="Overall monitoring risk score")

class EntityReport(BaseModel):
    name: str
    risk_score: int
    anomalies: List[str]
    entity_type: EntityType = Field(default_factory=EntityType, description="Entity classification and type analysis")
    property: Optional[PropertyData] = None
    court_data: Optional[CourtData] = Field(default_factory=CourtData, description="Court case information and litigation history")
    domain_data: Optional[DomainData] = Field(default_factory=DomainData, description="Domain and web presence analysis")
    officer_data: Optional[OfficerData] = Field(default_factory=OfficerData, description="Officer cross-reference analysis")
    grants_data: Optional[GrantsData] = Field(default_factory=GrantsData, description="Grant and contract funding analysis")
    monitoring_data: Optional[MonitoringData] = Field(default_factory=MonitoringData, description="Monitoring and change detection results")
    ownership_data: Optional['OwnershipData'] = Field(default_factory=lambda: None, description="Ownership chain and shell company analysis")
    source_links: Optional[Dict[str, str]] = Field(default_factory=dict, description="Relevant source document URLs")

class ExportRequest(BaseModel):
    entity_input: EntityInput = Field(..., description="Entity to analyze and export")
    export_format: Literal["pdf", "json"] = Field(..., description="Export format: PDF for reports, JSON for raw data")
    include_sections: List[str] = Field(
        default_factory=lambda: ["entity_info", "risk_score", "county_offices", "court_activity", "domain_info", "grants_data", "monitoring_data"],
        description="Sections to include in export",
        max_length=10
    )
    template_style: Optional[str] = Field("professional", description="Template style for PDF reports", max_length=50)
    
    @validator('include_sections')
    def validate_sections(cls, v):
        """Validate export sections."""
        valid_sections = [
            "entity_info", "risk_score", "county_offices", "court_activity", 
            "domain_info", "grants_data", "monitoring_data", "ownership_data"
        ]
        if v is None:
            return valid_sections[:7]  # Default sections
        
        # Check for invalid sections
        invalid_sections = [s for s in v if s not in valid_sections]
        if invalid_sections:
            raise ValueError(f"Invalid sections: {invalid_sections}")
        
        return v
    
    @validator('template_style', pre=True)
    def sanitize_template_style(cls, v):
        """Sanitize template style."""
        if v is None:
            return "professional"
        if isinstance(v, str):
            # Only allow alphanumeric and hyphens
            clean_style = re.sub(r'[^a-zA-Z0-9-]', '', v.strip())
            return clean_style if clean_style else "professional"
        return "professional"

class ExportResponse(BaseModel):
    success: bool = Field(..., description="Whether export was successful")
    file_name: str = Field(..., description="Generated file name")
    export_format: str = Field(..., description="Format of exported file")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    generated_at: str = Field(..., description="ISO timestamp when report was generated")
    entity_name: str = Field(..., description="Name of analyzed entity")
    risk_score: Optional[int] = Field(None, description="Overall risk score for quick reference")
    download_url: Optional[str] = Field(None, description="URL for file download")
    error_message: Optional[str] = Field(None, description="Error message if export failed")

# Ownership Analysis Models

class OfficerModel(BaseModel):
    name: str = Field(..., description="Officer full name")
    title: str = Field(..., description="Officer title/position")
    address: str = Field(..., description="Officer address")
    normalized_name: Optional[str] = Field(None, description="Normalized name for matching")
    normalized_address: Optional[str] = Field(None, description="Normalized address for matching")

class EntityModel(BaseModel):
    filing_id: str = Field(..., description="Unique filing ID")
    name: str = Field(..., description="Entity legal name")
    status: str = Field(..., description="Entity status (Active, Inactive, etc.)")
    entity_type: str = Field(..., description="Type of entity (Corporation, LLC, etc.)")
    date_filed: str = Field(..., description="Date entity was filed")
    officers: List[OfficerModel] = Field(default_factory=list, description="List of entity officers")
    registered_agent: Optional[str] = Field(None, description="Registered agent name")
    registered_address: Optional[str] = Field(None, description="Registered address")
    ownership_depth: int = Field(0, description="Depth in ownership chain")
    shell_company_score: float = Field(0.0, description="Shell company risk score")

class OwnershipChainModel(BaseModel):
    chain_id: int = Field(..., description="Unique chain identifier")
    root_entity: EntityModel = Field(..., description="Root entity in the chain")
    chain: List[EntityModel] = Field(..., description="Complete ownership chain")
    depth: int = Field(..., description="Chain depth (number of layers)")
    shell_indicators: List[str] = Field(default_factory=list, description="Shell company indicators found")
    risk_score: float = Field(..., description="Overall chain risk score (0-100)")
    obfuscation_patterns: List[str] = Field(default_factory=list, description="Ownership obfuscation patterns detected")

class OwnershipAnalysisRequest(BaseModel):
    entity_name: str = Field(..., min_length=1, max_length=200, description="Entity name to trace ownership for")
    max_depth: int = Field(5, ge=1, le=10, description="Maximum depth to trace ownership chains")
    include_inactive: bool = Field(False, description="Include inactive entities in analysis")
    similarity_threshold: float = Field(0.85, ge=0.5, le=1.0, description="Officer name similarity threshold")
    
    @validator('entity_name', pre=True)
    def sanitize_entity_name(cls, v):
        """Sanitize entity name for ownership analysis."""
        if v is None:
            raise ValueError("Entity name is required")
        if isinstance(v, str):
            # HTML escape and remove control characters
            v = html.escape(v.strip())
            v = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', v)
            if not v:
                raise ValueError("Entity name cannot be empty")
            return v
        raise ValueError("Entity name must be a string")
    
    @validator('max_depth')
    def validate_max_depth(cls, v):
        """Validate max depth is within safe limits."""
        if not isinstance(v, int):
            raise ValueError("Max depth must be an integer")
        if v < 1:
            raise ValueError("Max depth must be at least 1")
        if v > 10:
            raise ValueError("Max depth cannot exceed 10 (performance limit)")
        return v
    
    @validator('similarity_threshold')
    def validate_similarity_threshold(cls, v):
        """Validate similarity threshold is within valid range."""
        if not isinstance(v, (int, float)):
            raise ValueError("Similarity threshold must be a number")
        if v < 0.5:
            raise ValueError("Similarity threshold must be at least 0.5")
        if v > 1.0:
            raise ValueError("Similarity threshold cannot exceed 1.0")
        return float(v)

class ShellCompanyReport(BaseModel):
    entity_name: str = Field(..., description="Name of analyzed entity")
    analysis_date: str = Field(..., description="ISO timestamp of analysis")
    risk_assessment: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="Overall risk level")
    shell_company_probability: float = Field(..., ge=0.0, le=1.0, description="Probability entity is shell company")
    ownership_chains_found: int = Field(0, description="Number of ownership chains detected")
    deepest_chain_depth: int = Field(0, description="Depth of deepest ownership chain")
    total_shell_indicators: int = Field(0, description="Total shell company indicators found")
    total_obfuscation_patterns: int = Field(0, description="Total obfuscation patterns detected")
    max_risk_score: float = Field(0.0, description="Highest risk score among all chains")
    avg_risk_score: float = Field(0.0, description="Average risk score across all chains")
    ownership_chains: List[OwnershipChainModel] = Field(default_factory=list, description="Detailed ownership chains")
    summary: str = Field(..., description="Executive summary of findings")

class OwnershipData(BaseModel):
    ownership_analysis: Optional[ShellCompanyReport] = Field(None, description="Complete ownership analysis results")
    ownership_chains: List[OwnershipChainModel] = Field(default_factory=list, description="Detected ownership chains")
    shared_officers: List[Dict[str, Any]] = Field(default_factory=list, description="Officers shared across entities")
    risk_indicators: List[str] = Field(default_factory=list, description="Ownership-related risk indicators")
    shell_company_score: float = Field(0.0, description="Shell company probability score")
    obfuscation_detected: bool = Field(False, description="Whether ownership obfuscation was detected")
