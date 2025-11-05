"""
Trust Classification Module for LedgerTrace
Provides structured detection and classification of trust entities
"""

TRUST_KEYWORDS = {
    "revocable": "Revocable Trust",
    "irrevocable": "Irrevocable Trust", 
    "charitable": "Charitable Trust",
    "land": "Land Trust",
    "testamentary": "Testamentary Trust",
    "business trust": "Business Trust",
    "grantor": "Grantor Trust",
    "special needs": "Special Needs Trust",
    "real estate": "REIT (Trust)",
    "massachusetts trust": "Business Trust",
    "foreign": "Foreign Asset Trust",
    "living": "Living Trust",
    "family": "Family Trust",
    "investment": "Investment Trust",
    "unit": "Unit Trust",
    "voting": "Voting Trust",
    "asset protection": "Asset Protection Trust",
    "dynasty": "Dynasty Trust",
    "spendthrift": "Spendthrift Trust"
}

# High-risk trust indicators
HIGH_RISK_TRUST_TYPES = [
    "Business Trust",
    "Foreign Asset Trust", 
    "Asset Protection Trust"
]

# Trust types that should have EIN/501c3 status
REGULATED_TRUST_TYPES = [
    "Charitable Trust",
    "Investment Trust",
    "REIT (Trust)"
]

def classify_trust(name: str) -> dict:
    """
    Classify trust entity by name and return structured metadata
    
    Args:
        name: Entity name to analyze
        
    Returns:
        dict: Classification results with trust types, flags, and metadata
    """
    if not name:
        return {
            "is_trust": False,
            "trust_types": [],
            "match_terms": [],
            "risk_indicators": []
        }
        
    name_lower = name.lower().strip()
    
    # Check if entity mentions "trust" at all
    is_trust = "trust" in name_lower
    
    # Find matching trust type keywords
    matched_types = []
    matched_terms = []
    
    for keyword, trust_type in TRUST_KEYWORDS.items():
        if keyword in name_lower:
            matched_types.append(trust_type)
            matched_terms.append(keyword)
    
    # If it says "trust" but no specific type found, classify as generic
    if is_trust and not matched_types:
        matched_types = ["Generic Trust"]
    
    # Identify risk indicators
    risk_indicators = []
    
    # Check for high-risk trust types
    for trust_type in matched_types:
        if trust_type in HIGH_RISK_TRUST_TYPES:
            risk_indicators.append(f"high_risk_type:{trust_type}")
    
    # Check for regulated trust types
    for trust_type in matched_types:
        if trust_type in REGULATED_TRUST_TYPES:
            risk_indicators.append(f"requires_regulation:{trust_type}")
    
    # Check for suspicious naming patterns
    suspicious_patterns = [
        ("llc", "trust_with_llc"),
        ("inc", "trust_with_corp"),
        ("corp", "trust_with_corp"),
        ("ltd", "trust_with_ltd"),
        ("offshore", "offshore_trust"),
        ("international", "international_trust"),
        ("privacy", "privacy_trust"),
        ("anonymous", "anonymous_trust")
    ]
    
    for pattern, indicator in suspicious_patterns:
        if pattern in name_lower and is_trust:
            risk_indicators.append(indicator)
    
    return {
        "is_trust": is_trust,
        "trust_types": matched_types,
        "match_terms": matched_terms,
        "risk_indicators": risk_indicators,
        "requires_regulation": any(t in REGULATED_TRUST_TYPES for t in matched_types),
        "high_risk": any(t in HIGH_RISK_TRUST_TYPES for t in matched_types)
    }

def get_trust_risk_flags(classification: dict, has_ein: bool = False) -> list:
    """
    Generate specific red flags based on trust classification
    
    Args:
        classification: Result from classify_trust()
        has_ein: Whether entity has EIN provided
        
    Returns:
        list: List of red flag strings
    """
    flags = []
    
    if not classification["is_trust"]:
        return flags
    
    # High-risk trust type flags
    if classification["high_risk"]:
        risk_types = [t for t in classification["trust_types"] if t in HIGH_RISK_TRUST_TYPES]
        flags.append(f"⚠️ Entity appears to be a high-risk trust type: {', '.join(risk_types)}")
    
    # Regulatory compliance flags
    if classification["requires_regulation"] and not has_ein:
        regulated_types = [t for t in classification["trust_types"] if t in REGULATED_TRUST_TYPES]
        flags.append(f"⚠️ {', '.join(regulated_types)} missing required EIN or regulatory filing")
    
    # Suspicious structure flags
    for indicator in classification["risk_indicators"]:
        if indicator.startswith("trust_with_"):
            entity_type = indicator.split(":")[-1] if ":" in indicator else indicator.replace("trust_with_", "")
            flags.append(f"⚠️ Unusual trust structure: combines trust with {entity_type.upper()}")
        elif indicator.startswith("offshore") or indicator.startswith("international"):
            flags.append("⚠️ International or offshore trust structure detected")
        elif indicator.startswith("privacy") or indicator.startswith("anonymous"):
            flags.append("⚠️ Privacy-focused trust name may indicate asset concealment")
    
    # Generic trust without specific classification
    if "Generic Trust" in classification["trust_types"] and len(classification["trust_types"]) == 1:
        flags.append("⚠️ Generic trust entity without clear classification or purpose")
    
    return flags

def get_trust_source_links(entity_name: str, classification: dict) -> dict:
    """
    Generate relevant source document links for trust entities
    
    Args:
        entity_name: Name of the entity
        classification: Trust classification results
        
    Returns:
        dict: Source links relevant to trust type
    """
    encoded_name = entity_name.replace(" ", "%20")
    sources = {}
    
    # Standard business/corporate sources
    sources["sunbiz"] = f"http://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults?InquiryType=EntityName&SearchTerm={encoded_name}"
    
    # If it's a charitable trust, include IRS 990 lookup
    if "Charitable Trust" in classification.get("trust_types", []):
        sources["irs_990"] = f"https://apps.irs.gov/app/eos/allSearch?names={encoded_name}"
        sources["charity_navigator"] = f"https://www.charitynavigator.org/index.cfm?bay=search.summary&orgname={encoded_name}"
    
    # If it's an investment trust or REIT, include SEC lookup
    if any(t in ["Investment Trust", "REIT (Trust)"] for t in classification.get("trust_types", [])):
        sources["sec_edgar"] = f"https://www.sec.gov/cgi-bin/browse-edgar?company={encoded_name}&match=contains"
    
    # Court records for probate/testamentary trusts
    if "Testamentary Trust" in classification.get("trust_types", []):
        sources["court_records"] = f"https://www.courtrecords.org/search?name={encoded_name}"
    
    return sources