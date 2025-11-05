from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class EntityInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Entity name to analyze")
    address: Optional[str] = Field(None, max_length=500, description="Entity address for property analysis")
    ein: Optional[str] = Field(None, max_length=12, pattern=r"^\d{2}-?\d{7}$", description="Federal EIN number")
    officers: Optional[List[str]] = Field(default_factory=list, max_items=20, description="List of officers")
    county: Optional[str] = Field(None, max_length=50, description="Florida county name")

class PropertyData(BaseModel):
    county: str
    address: str
    owner_name: str
    land_use: str
    market_value: str
    delinquent_taxes: bool
    source_url: str

class EntityType(BaseModel):
    is_trust: bool = Field(False, description="Whether entity is classified as a trust")
    trust_types: List[str] = Field(default_factory=list, description="Specific trust type classifications")
    match_terms: List[str] = Field(default_factory=list, description="Keywords that triggered classification")
    risk_indicators: List[str] = Field(default_factory=list, description="Risk indicators found in entity structure")
    requires_regulation: bool = Field(False, description="Whether trust type requires regulatory filing")
    high_risk: bool = Field(False, description="Whether trust is classified as high-risk type")

class EntityReport(BaseModel):
    name: str
    risk_score: int
    anomalies: List[str]
    entity_type: EntityType = Field(default_factory=EntityType, description="Entity classification and type analysis")
    property: Optional[PropertyData] = None
    source_links: Optional[Dict[str, str]] = Field(default_factory=dict, description="Relevant source document URLs")
