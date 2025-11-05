"""
Court Case Checker Module for LedgerTrace
Provides detection and analysis of court cases involving entities
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import quote_plus

# Mock database of court cases for demonstration
# In production, this would integrate with actual clerk of court APIs
MOCK_COURT_CASES = {
    # Foreclosure cases
    "Sunshine Holdings LLC": {
        "case_type": "Foreclosure",
        "case_number": "2024-CA-001234",
        "status": "Open", 
        "filed_date": "2024-11-01",
        "county": "Marion",
        "plaintiff": "First National Bank",
        "property_address": "123 Investment Blvd, Ocala, FL",
        "amount": "$450,000"
    },
    "Florida Investment Properties LLC": {
        "case_type": "Foreclosure", 
        "case_number": "2024-CA-005678",
        "status": "Judgment",
        "filed_date": "2024-08-15",
        "county": "Orange",
        "plaintiff": "Community Trust Bank",
        "property_address": "456 Commerce St, Orlando, FL", 
        "amount": "$275,000"
    },
    # Tax lien cases
    "Coastal Development Trust": {
        "case_type": "Tax Lien",
        "case_number": "2024-TX-002134", 
        "status": "Open",
        "filed_date": "2024-10-15",
        "county": "Brevard",
        "plaintiff": "Brevard County Tax Collector",
        "property_address": "789 Beachfront Dr, Melbourne, FL",
        "amount": "$15,750"
    },
    # Civil litigation
    "Business Investment Trust LLC": {
        "case_type": "Civil Litigation",
        "case_number": "2024-CC-003456",
        "status": "Open",
        "filed_date": "2024-09-20", 
        "county": "Hillsborough",
        "plaintiff": "State of Florida DBPR",
        "description": "Unlicensed contractor violations",
        "amount": "$25,000"
    },
    # Bankruptcy cases
    "Offshore Holdings Trust": {
        "case_type": "Bankruptcy",
        "case_number": "2024-BK-001122",
        "status": "Active",
        "filed_date": "2024-07-30",
        "county": "Federal - Middle District FL", 
        "chapter": "Chapter 11",
        "assets": "$1,200,000",
        "liabilities": "$2,400,000"
    }
}

# County clerk search URLs (mock for demonstration)
COUNTY_CLERK_URLS = {
    "marion": "https://www.marioncountyclerk.org/court-records/search",
    "orange": "https://myorangeclerk.com/case-search", 
    "brevard": "https://brevardclerk.us/court-records",
    "hillsborough": "https://hillsclerk.com/records/search",
    "federal": "https://pacer.uscourts.gov"
}

def check_court_cases(entity_name: str, county: str = None, property_address: str = None) -> Dict:
    """
    Check for court cases involving the entity
    
    Args:
        entity_name: Name of entity to search
        county: County to focus search (optional)
        property_address: Property address to cross-reference (optional)
        
    Returns:
        dict: Court case information and risk indicators
    """
    if not entity_name:
        return {"cases": [], "risk_indicators": []}
    
    # Search for direct entity matches
    cases = []
    risk_indicators = []
    
    # Check mock database for entity name matches
    entity_name_clean = entity_name.strip()
    for name_key, case_data in MOCK_COURT_CASES.items():
        if _entity_name_match(entity_name_clean, name_key):
            case_info = case_data.copy()
            case_info["search_url"] = _generate_clerk_search_url(case_data.get("county", ""), entity_name)
            cases.append(case_info)
    
    # Check for property address matches if provided
    if property_address:
        property_cases = _check_property_cases(property_address)
        cases.extend(property_cases)
    
    # Generate risk indicators based on found cases
    risk_indicators = _analyze_case_risk(cases, entity_name)
    
    return {
        "cases": cases,
        "risk_indicators": risk_indicators,
        "case_count": len(cases),
        "has_foreclosure": any(c.get("case_type") == "Foreclosure" for c in cases),
        "has_tax_lien": any(c.get("case_type") == "Tax Lien" for c in cases),
        "has_civil": any(c.get("case_type") == "Civil Litigation" for c in cases),
        "has_bankruptcy": any(c.get("case_type") == "Bankruptcy" for c in cases)
    }

def _entity_name_match(search_name: str, database_name: str) -> bool:
    """Check if entity names match with fuzzy logic"""
    search_clean = re.sub(r'[^\w\s]', '', search_name.lower())
    db_clean = re.sub(r'[^\w\s]', '', database_name.lower())
    
    # Exact match
    if search_clean == db_clean:
        return True
    
    # Partial match for LLCs, Trusts, etc.
    search_words = set(search_clean.split())
    db_words = set(db_clean.split())
    
    # Remove common entity suffixes for comparison
    entity_suffixes = {'llc', 'inc', 'corp', 'trust', 'ltd', 'foundation'}
    search_core = search_words - entity_suffixes
    db_core = db_words - entity_suffixes
    
    if len(search_core) > 0 and len(db_core) > 0:
        # Check if most core words match
        intersection = search_core & db_core
        return len(intersection) >= min(len(search_core), len(db_core)) * 0.7
    
    return False

def _check_property_cases(property_address: str) -> List[Dict]:
    """Check for court cases involving a specific property"""
    property_cases = []
    
    for case_data in MOCK_COURT_CASES.values():
        if "property_address" in case_data:
            # Simple address matching - in production would be more sophisticated
            if _address_match(property_address, case_data["property_address"]):
                case_info = case_data.copy()
                case_info["match_type"] = "property_address"
                property_cases.append(case_info)
    
    return property_cases

def _address_match(search_addr: str, case_addr: str) -> bool:
    """Simple address matching logic"""
    if not search_addr or not case_addr:
        return False
    
    # Extract street numbers and names
    search_clean = re.sub(r'[^\w\s]', ' ', search_addr.lower())
    case_clean = re.sub(r'[^\w\s]', ' ', case_addr.lower())
    
    search_words = search_clean.split()
    case_words = case_clean.split()
    
    # Look for matching street number and street name
    matching_words = set(search_words) & set(case_words)
    return len(matching_words) >= 2  # At least number + street name

def _analyze_case_risk(cases: List[Dict], entity_name: str) -> List[str]:
    """Analyze court cases to generate risk indicators"""
    indicators = []
    
    if not cases:
        return indicators
    
    # Count different case types
    foreclosure_count = sum(1 for c in cases if c.get("case_type") == "Foreclosure")
    tax_lien_count = sum(1 for c in cases if c.get("case_type") == "Tax Lien") 
    civil_count = sum(1 for c in cases if c.get("case_type") == "Civil Litigation")
    bankruptcy_count = sum(1 for c in cases if c.get("case_type") == "Bankruptcy")
    
    # Generate risk indicators
    if foreclosure_count > 0:
        indicators.append(f"active_foreclosure_cases:{foreclosure_count}")
    
    if tax_lien_count > 0:
        indicators.append(f"tax_lien_cases:{tax_lien_count}")
    
    if civil_count > 0:
        indicators.append(f"civil_litigation_cases:{civil_count}")
        
    if bankruptcy_count > 0:
        indicators.append(f"bankruptcy_cases:{bankruptcy_count}")
    
    # Check for multiple case types (pattern of financial distress)
    case_types = set(c.get("case_type") for c in cases if c.get("case_type"))
    if len(case_types) >= 2:
        indicators.append("multiple_case_types")
    
    # Check for recent cases (within 6 months)
    recent_cases = []
    cutoff_date = datetime.now() - timedelta(days=180)
    
    for case in cases:
        try:
            case_date = datetime.strptime(case.get("filed_date", ""), "%Y-%m-%d")
            if case_date >= cutoff_date:
                recent_cases.append(case)
        except ValueError:
            continue
    
    if len(recent_cases) > 0:
        indicators.append(f"recent_court_activity:{len(recent_cases)}")
    
    # Check for high-dollar cases
    high_dollar_cases = []
    for case in cases:
        amount_str = case.get("amount", "")
        if amount_str:
            try:
                # Extract numeric value from amount string
                amount_clean = re.sub(r'[^\d.]', '', amount_str)
                if amount_clean:
                    amount = float(amount_clean)
                    if amount >= 100000:  # $100k threshold
                        high_dollar_cases.append(case)
            except ValueError:
                continue
    
    if high_dollar_cases:
        indicators.append(f"high_dollar_cases:{len(high_dollar_cases)}")
    
    return indicators

def _generate_clerk_search_url(county: str, entity_name: str) -> str:
    """Generate URL to clerk of court search for the entity"""
    if not county:
        return ""
    
    county_clean = county.lower().replace(" county", "").replace(" ", "")
    base_url = COUNTY_CLERK_URLS.get(county_clean, "")
    
    if base_url:
        encoded_name = quote_plus(entity_name)
        return f"{base_url}?q={encoded_name}"
    
    return f"https://www.google.com/search?q=\"{quote_plus(entity_name)}\" {quote_plus(county)} clerk court"

def get_court_risk_flags(court_data: Dict) -> List[str]:
    """
    Generate specific red flags based on court case analysis
    
    Args:
        court_data: Result from check_court_cases()
        
    Returns:
        list: List of red flag strings
    """
    flags = []
    
    if not court_data.get("cases"):
        return flags
    
    cases = court_data["cases"]
    risk_indicators = court_data.get("risk_indicators", [])
    
    # Foreclosure flags
    if court_data.get("has_foreclosure"):
        open_foreclosures = [c for c in cases if c.get("case_type") == "Foreclosure" and c.get("status") == "Open"]
        if open_foreclosures:
            flags.append(f"⚠️ Entity involved in {len(open_foreclosures)} active foreclosure case(s)")
    
    # Tax lien flags  
    if court_data.get("has_tax_lien"):
        flags.append("⚠️ Entity has outstanding tax lien cases")
    
    # Civil litigation flags
    if court_data.get("has_civil"):
        civil_cases = [c for c in cases if c.get("case_type") == "Civil Litigation"]
        for case in civil_cases:
            if "DBPR" in case.get("plaintiff", ""):
                flags.append("⚠️ Entity facing regulatory action from Florida DBPR")
            elif case.get("status") == "Open":
                flags.append("⚠️ Entity involved in active civil litigation")
    
    # Bankruptcy flags
    if court_data.get("has_bankruptcy"):
        bankruptcy_cases = [c for c in cases if c.get("case_type") == "Bankruptcy"]
        for case in bankruptcy_cases:
            if case.get("status") == "Active":
                chapter = case.get("chapter", "Unknown")
                flags.append(f"⚠️ Entity in active {chapter} bankruptcy proceedings")
    
    # Pattern flags
    for indicator in risk_indicators:
        if indicator == "multiple_case_types":
            flags.append("⚠️ Entity shows pattern of financial and legal distress")
        elif indicator.startswith("recent_court_activity"):
            count = indicator.split(":")[-1]
            flags.append(f"⚠️ Entity has {count} recent court case(s) within 6 months")
        elif indicator.startswith("high_dollar_cases"):
            count = indicator.split(":")[-1] 
            flags.append(f"⚠️ Entity involved in {count} high-dollar court case(s) (>$100k)")
    
    return flags