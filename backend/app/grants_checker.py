"""
Grant and Contract Database Integration for LedgerTrace
Checks federal/state grants, contracts, and funding awards
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import quote_plus

# Mock grant and contract database
# In production, this would integrate with USASpending.gov API, grants.gov, state databases
MOCK_GRANTS_DATABASE = {
    "sunshine_holdings_llc": {
        "entity_name": "Sunshine Holdings LLC",
        "grants": [
            {
                "award_id": "FEMA-FL-2024-001234",
                "title": "Hurricane Recovery Housing Initiative", 
                "agency": "FEMA",
                "award_date": "2024-10-15",
                "amount": "$2,500,000",
                "type": "Grant",
                "status": "Active",
                "period_start": "2024-10-15",
                "period_end": "2025-10-14",
                "description": "Emergency housing assistance for hurricane victims",
                "compliance_status": "Under Review"
            }
        ],
        "contracts": [
            {
                "contract_id": "FL-DOT-2024-5678",
                "title": "Emergency Road Repair Services",
                "agency": "Florida Department of Transportation", 
                "award_date": "2024-11-01",
                "amount": "$450,000",
                "type": "Contract",
                "status": "Active",
                "period_start": "2024-11-01",
                "period_end": "2025-04-30",
                "description": "Post-hurricane infrastructure repair",
                "compliance_status": "Current"
            }
        ]
    },
    "florida_educational_charitable_trust": {
        "entity_name": "Florida Educational Charitable Trust",
        "grants": [
            {
                "award_id": "ED-FL-2024-9876",
                "title": "Rural Education Technology Initiative",
                "agency": "U.S. Department of Education",
                "award_date": "2024-08-01", 
                "amount": "$750,000",
                "type": "Grant",
                "status": "Active",
                "period_start": "2024-08-01",
                "period_end": "2026-07-31",
                "description": "Technology access for underserved rural schools",
                "compliance_status": "Current"
            },
            {
                "award_id": "FL-DOE-2024-3333",
                "title": "Teacher Professional Development Program",
                "agency": "Florida Department of Education",
                "award_date": "2024-09-15",
                "amount": "$125,000", 
                "type": "Grant",
                "status": "Active",
                "period_start": "2024-09-15",
                "period_end": "2025-08-31",
                "description": "Professional development for rural teachers",
                "compliance_status": "Current"
            }
        ],
        "contracts": []
    },
    "business_investment_trust_llc": {
        "entity_name": "Business Investment Trust LLC",
        "grants": [
            {
                "award_id": "SBA-FL-2024-7890",
                "title": "Small Business Recovery Loan Program",
                "agency": "Small Business Administration",
                "award_date": "2024-06-01",
                "amount": "$350,000",
                "type": "Loan/Grant Hybrid",
                "status": "Under Investigation",
                "period_start": "2024-06-01", 
                "period_end": "2027-05-31",
                "description": "COVID-19 business recovery assistance",
                "compliance_status": "Non-Compliant - Misuse Investigation"
            }
        ],
        "contracts": [
            {
                "contract_id": "FL-DBPR-2024-1111",
                "title": "Construction Oversight Services",
                "agency": "Florida DBPR",
                "award_date": "2024-07-15",
                "amount": "$75,000",
                "type": "Contract",
                "status": "Terminated",
                "period_start": "2024-07-15",
                "period_end": "2024-09-20",
                "description": "Construction project oversight and inspection",
                "compliance_status": "Breach of Contract",
                "termination_reason": "Unlicensed contractor violations"
            }
        ]
    }
}

# Mock suspicious award patterns
SUSPICIOUS_GRANT_PATTERNS = {
    "rapid_multiple_awards": {
        "description": "Multiple awards in short timeframe",
        "threshold": 2,
        "timeframe_days": 90
    },
    "award_during_litigation": {
        "description": "Received awards while under investigation",
        "status_keywords": ["investigation", "review", "audit", "non-compliant"]
    },
    "high_dollar_new_entity": {
        "description": "Large award to recently formed entity",
        "amount_threshold": 1000000,
        "entity_age_days": 365
    }
}

def analyze_grants_contracts(entity_name: str, entity_formation_date: str = None) -> Dict:
    """
    Analyze entity's grant and contract history
    
    Args:
        entity_name: Name of entity to analyze
        entity_formation_date: When entity was formed (optional)
        
    Returns:
        dict: Grant and contract analysis results
    """
    if not entity_name:
        return {
            "grants": [],
            "contracts": [],
            "risk_indicators": [],
            "total_funding": 0
        }
    
    # Look up entity in grants database
    entity_key = _normalize_entity_name_for_lookup(entity_name)
    entity_data = MOCK_GRANTS_DATABASE.get(entity_key, {})
    
    grants = entity_data.get("grants", [])
    contracts = entity_data.get("contracts", [])
    
    # Calculate total funding
    total_funding = 0
    for award in grants + contracts:
        amount_str = award.get("amount", "$0")
        amount_numeric = _parse_dollar_amount(amount_str)
        total_funding += amount_numeric
    
    # Analyze risk patterns
    risk_indicators = _analyze_funding_risks(grants, contracts, entity_name, entity_formation_date)
    
    # Generate summary statistics
    active_grants = [g for g in grants if g.get("status") == "Active"]
    active_contracts = [c for c in contracts if c.get("status") == "Active"]
    problematic_awards = [a for a in grants + contracts if 
                         a.get("compliance_status", "").lower() in ["non-compliant", "under review", "breach of contract"]]
    
    return {
        "grants": grants,
        "contracts": contracts,
        "total_awards": len(grants) + len(contracts),
        "active_grants": len(active_grants),
        "active_contracts": len(active_contracts),
        "total_funding": total_funding,
        "problematic_awards": len(problematic_awards),
        "risk_indicators": risk_indicators,
        "has_federal_funding": any(_is_federal_agency(a.get("agency", "")) for a in grants + contracts),
        "has_state_funding": any(_is_state_agency(a.get("agency", "")) for a in grants + contracts),
        "has_compliance_issues": len(problematic_awards) > 0
    }

def _normalize_entity_name_for_lookup(entity_name: str) -> str:
    """Normalize entity name for database lookup"""
    # Convert to lowercase and replace spaces/punctuation with underscores
    normalized = re.sub(r'[^\w\s]', '', entity_name.lower())
    normalized = re.sub(r'\s+', '_', normalized)
    return normalized

def _parse_dollar_amount(amount_str: str) -> float:
    """Parse dollar amount string to numeric value"""
    if not amount_str:
        return 0.0
    
    # Remove currency symbols and commas
    clean_amount = re.sub(r'[^\d.]', '', amount_str)
    
    try:
        return float(clean_amount) if clean_amount else 0.0
    except ValueError:
        return 0.0

def _is_federal_agency(agency_name: str) -> bool:
    """Check if agency is federal"""
    federal_indicators = [
        "u.s.", "united states", "federal", "fema", "department of", 
        "sba", "small business administration", "irs", "treasury"
    ]
    return any(indicator in agency_name.lower() for indicator in federal_indicators)

def _is_state_agency(agency_name: str) -> bool:
    """Check if agency is state-level"""
    state_indicators = [
        "florida", "fl", "state of", "department of transportation", 
        "dbpr", "doe", "department of education"
    ]
    return any(indicator in agency_name.lower() for indicator in state_indicators)

def _analyze_funding_risks(grants: List[Dict], contracts: List[Dict], entity_name: str, formation_date: str = None) -> List[str]:
    """Analyze risk patterns in funding history"""
    indicators = []
    
    all_awards = grants + contracts
    
    if not all_awards:
        return indicators
    
    # Check for rapid multiple awards
    recent_awards = []
    cutoff_date = datetime.now() - timedelta(days=SUSPICIOUS_GRANT_PATTERNS["rapid_multiple_awards"]["timeframe_days"])
    
    for award in all_awards:
        try:
            award_date = datetime.strptime(award.get("award_date", ""), "%Y-%m-%d")
            if award_date >= cutoff_date:
                recent_awards.append(award)
        except ValueError:
            continue
    
    if len(recent_awards) >= SUSPICIOUS_GRANT_PATTERNS["rapid_multiple_awards"]["threshold"]:
        indicators.append(f"rapid_multiple_awards:{len(recent_awards)}")
    
    # Check for awards during litigation/investigation
    for award in all_awards:
        compliance_status = award.get("compliance_status", "").lower()
        for keyword in SUSPICIOUS_GRANT_PATTERNS["award_during_litigation"]["status_keywords"]:
            if keyword in compliance_status:
                indicators.append(f"award_during_investigation:{award.get('award_id', 'unknown')}")
                break
    
    # Check for high-dollar awards to new entities
    if formation_date:
        try:
            formation_dt = datetime.strptime(formation_date, "%Y-%m-%d")
            for award in all_awards:
                award_date = datetime.strptime(award.get("award_date", ""), "%Y-%m-%d")
                days_since_formation = (award_date - formation_dt).days
                award_amount = _parse_dollar_amount(award.get("amount", "$0"))
                
                if (days_since_formation <= SUSPICIOUS_GRANT_PATTERNS["high_dollar_new_entity"]["entity_age_days"] and
                    award_amount >= SUSPICIOUS_GRANT_PATTERNS["high_dollar_new_entity"]["amount_threshold"]):
                    indicators.append(f"large_award_new_entity:{award.get('award_id', 'unknown')}")
        except ValueError:
            pass
    
    # Check for terminated/breached contracts
    terminated_contracts = [c for c in contracts if c.get("status") in ["Terminated", "Breached"]]
    if terminated_contracts:
        indicators.append(f"terminated_contracts:{len(terminated_contracts)}")
    
    # Check for compliance issues
    non_compliant_awards = [a for a in all_awards if "non-compliant" in a.get("compliance_status", "").lower()]
    if non_compliant_awards:
        indicators.append(f"compliance_violations:{len(non_compliant_awards)}")
    
    # Check for overlapping award periods (possible double-dipping)
    active_federal_awards = [a for a in all_awards if 
                           _is_federal_agency(a.get("agency", "")) and a.get("status") == "Active"]
    if len(active_federal_awards) >= 2:
        indicators.append(f"multiple_active_federal_awards:{len(active_federal_awards)}")
    
    return indicators

def get_grants_risk_flags(grants_data: Dict) -> List[str]:
    """
    Generate specific red flags based on grants/contracts analysis
    
    Args:
        grants_data: Result from analyze_grants_contracts()
        
    Returns:
        list: List of red flag strings
    """
    flags = []
    
    grants = grants_data.get("grants", [])
    contracts = grants_data.get("contracts", [])
    risk_indicators = grants_data.get("risk_indicators", [])
    
    # No funding history
    if not grants and not contracts:
        return flags
    
    # Compliance issue flags
    if grants_data.get("has_compliance_issues"):
        problematic_count = grants_data.get("problematic_awards", 0)
        flags.append(f"⚠️ Entity has {problematic_count} award(s) with compliance issues")
    
    # Specific compliance problems
    for award in grants + contracts:
        compliance_status = award.get("compliance_status", "")
        if "non-compliant" in compliance_status.lower():
            award_title = award.get("title", "Unknown Award")
            flags.append(f"⚠️ Non-compliant award: {award_title}")
        elif "breach of contract" in compliance_status.lower():
            award_title = award.get("title", "Unknown Contract")
            flags.append(f"⚠️ Breached contract: {award_title}")
        elif "investigation" in compliance_status.lower():
            award_title = award.get("title", "Unknown Award")
            flags.append(f"⚠️ Award under investigation: {award_title}")
    
    # Pattern-based flags
    for indicator in risk_indicators:
        if indicator.startswith("rapid_multiple_awards"):
            count = indicator.split(":")[-1]
            flags.append(f"⚠️ Received {count} awards within 90 days")
        
        elif indicator.startswith("award_during_investigation"):
            award_id = indicator.split(":")[-1]
            flags.append(f"⚠️ Received award while under investigation: {award_id}")
        
        elif indicator.startswith("large_award_new_entity"):
            award_id = indicator.split(":")[-1]
            flags.append(f"⚠️ Large award to recently formed entity: {award_id}")
        
        elif indicator.startswith("terminated_contracts"):
            count = indicator.split(":")[-1]
            flags.append(f"⚠️ {count} contract(s) terminated for cause")
        
        elif indicator.startswith("compliance_violations"):
            count = indicator.split(":")[-1]
            flags.append(f"⚠️ {count} award(s) with compliance violations")
        
        elif indicator.startswith("multiple_active_federal_awards"):
            count = indicator.split(":")[-1]
            flags.append(f"⚠️ {count} simultaneous active federal awards (possible overlap)")
    
    return flags

def generate_funding_source_links(entity_name: str, grants_data: Dict) -> Dict[str, str]:
    """Generate links to funding databases and oversight sites"""
    links = {}
    
    encoded_name = quote_plus(entity_name)
    
    # Federal databases
    if grants_data.get("has_federal_funding"):
        links["usa_spending"] = f"https://www.usaspending.gov/search/?hash=142c21e7e1b6e9a87b04d84938c84bb9"
        links["grants_gov"] = f"https://www.grants.gov/web/grants/search-grants.html?keywords={encoded_name}"
        links["sam_gov"] = f"https://sam.gov/search?keywords={encoded_name}"
    
    # State databases  
    if grants_data.get("has_state_funding"):
        links["fl_transparency"] = f"https://floridahasarighttoknow.myflorida.com/search?q={encoded_name}"
        links["fl_contracts"] = f"https://www.dms.myflorida.com/business_operations/state_purchasing"
    
    # Oversight and audit sites
    if grants_data.get("has_compliance_issues"):
        links["oig_reports"] = f"https://oig.hhs.gov/reports-and-publications/"
        links["gao_reports"] = f"https://www.gao.gov/reports-testimonies"
    
    return links