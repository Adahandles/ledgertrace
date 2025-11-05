"""
Officer Cross-Reference Module for LedgerTrace  
Tracks officers, directors, and key personnel across multiple entities
"""

import re
from datetime import datetime
from typing import Dict, List, Set, Tuple
from difflib import SequenceMatcher

# Mock officer database for demonstration
# In production, this would integrate with Sunbiz API, SEC filings, etc.
MOCK_OFFICER_DATABASE = {
    "john_smith": {
        "name": "John Smith",
        "variations": ["John A Smith", "J. Smith", "John Smith Jr"],
        "entities": [
            {
                "entity_name": "Sunshine Holdings LLC", 
                "role": "Managing Member",
                "start_date": "2024-01-15",
                "status": "Active",
                "filing_source": "FL Sunbiz"
            },
            {
                "entity_name": "Coastal Development Trust",
                "role": "Trustee", 
                "start_date": "2024-03-10",
                "status": "Active",
                "filing_source": "FL Sunbiz"
            },
            {
                "entity_name": "Florida Investment Properties LLC",
                "role": "Member",
                "start_date": "2023-11-20",
                "status": "Resigned",
                "end_date": "2024-08-15",
                "filing_source": "FL Sunbiz"
            }
        ],
        "addresses": [
            "123 Investment Blvd, Ocala, FL 34471",
            "456 Business Park Dr, Tampa, FL 33602"
        ],
        "business_affiliations": [
            "Licensed Real Estate Broker - FL",
            "Registered Investment Advisor"
        ]
    },
    "michael_johnson": {
        "name": "Michael Johnson",
        "variations": ["Michael A Johnson", "Mike Johnson", "M. Johnson"],
        "entities": [
            {
                "entity_name": "Business Investment Trust LLC",
                "role": "President",
                "start_date": "2024-09-01", 
                "status": "Active",
                "filing_source": "FL Sunbiz"
            },
            {
                "entity_name": "Offshore Holdings Trust",
                "role": "Managing Director",
                "start_date": "2024-07-15",
                "status": "Active", 
                "filing_source": "Federal Filing"
            },
            {
                "entity_name": "Investment Advisory Services Inc",
                "role": "CEO",
                "start_date": "2023-05-01",
                "status": "Active",
                "filing_source": "FL Sunbiz"
            }
        ],
        "addresses": [
            "789 Financial Plaza, Miami, FL 33101",
            "PO Box 12345, Cayman Islands"
        ],
        "business_affiliations": [
            "CPA License - FL (Suspended 2024)",
            "Series 7 Securities License"
        ]
    },
    "sarah_williams": {
        "name": "Sarah Williams", 
        "variations": ["Sarah M Williams", "S. Williams", "Sarah Martinez-Williams"],
        "entities": [
            {
                "entity_name": "Florida Educational Charitable Trust",
                "role": "Executive Director",
                "start_date": "2024-02-01",
                "status": "Active",
                "filing_source": "IRS 990"
            },
            {
                "entity_name": "Community Development Foundation",
                "role": "Board Member",
                "start_date": "2023-08-15", 
                "status": "Active",
                "filing_source": "FL Sunbiz"
            }
        ],
        "addresses": [
            "321 Charity Lane, Gainesville, FL 32601"
        ],
        "business_affiliations": [
            "Nonprofit Management Certificate"
        ]
    }
}

# Mock problematic officer patterns
PROBLEMATIC_OFFICER_PATTERNS = {
    "serial_entity_creator": {
        "description": "Creates multiple entities in short timeframe",
        "threshold": 3,
        "timeframe_days": 365
    },
    "shell_company_indicator": {
        "description": "Officer in multiple entities with same address",
        "threshold": 2
    },
    "regulatory_issues": {
        "description": "Officer with suspended licenses or sanctions",
        "keywords": ["suspended", "revoked", "sanctioned", "violation"]
    }
}

def analyze_officer_connections(entity_officers: List[str], entity_name: str) -> Dict:
    """
    Analyze officer connections across entities
    
    Args:
        entity_officers: List of officer names for the entity
        entity_name: Name of the entity being analyzed
        
    Returns:
        dict: Officer analysis results with cross-references
    """
    if not entity_officers:
        return {
            "officers": [],
            "cross_references": [],
            "risk_indicators": [],
            "total_entities_connected": 0
        }
    
    officer_analysis = []
    all_connected_entities = set()
    risk_indicators = []
    
    # Analyze each officer
    for officer_name in entity_officers:
        if not officer_name or not officer_name.strip():
            continue
            
        officer_data = _find_officer_matches(officer_name)
        if officer_data:
            # Get entities this officer is connected to
            officer_entities = officer_data.get("entities", [])
            connected_entities = [e["entity_name"] for e in officer_entities if e["entity_name"] != entity_name]
            all_connected_entities.update(connected_entities)
            
            # Analyze risk patterns for this officer
            officer_risks = _analyze_officer_risks(officer_data, entity_name)
            risk_indicators.extend(officer_risks)
            
            officer_summary = {
                "name": officer_name,
                "matched_name": officer_data["name"],
                "confidence": _calculate_name_match_confidence(officer_name, officer_data["name"]),
                "total_entities": len(officer_entities),
                "active_entities": len([e for e in officer_entities if e["status"] == "Active"]),
                "connected_entities": connected_entities,
                "addresses": officer_data.get("addresses", []),
                "business_affiliations": officer_data.get("business_affiliations", []),
                "risk_flags": _get_officer_risk_flags(officer_data)
            }
            officer_analysis.append(officer_summary)
    
    # Generate cross-reference analysis
    cross_references = _generate_cross_references(officer_analysis, entity_name)
    
    # Overall risk assessment
    overall_risks = _assess_overall_officer_risks(officer_analysis, cross_references)
    risk_indicators.extend(overall_risks)
    
    return {
        "officers": officer_analysis,
        "cross_references": cross_references,
        "risk_indicators": list(set(risk_indicators)),  # Remove duplicates
        "total_entities_connected": len(all_connected_entities),
        "has_shared_officers": len(cross_references) > 0,
        "has_problematic_officers": any("problematic" in r for r in risk_indicators)
    }

def _find_officer_matches(officer_name: str) -> Dict:
    """Find officer matches in the database using fuzzy matching"""
    officer_name_clean = _normalize_name(officer_name)
    
    best_match = None
    best_score = 0.0
    
    for officer_key, officer_data in MOCK_OFFICER_DATABASE.items():
        # Check main name and variations
        names_to_check = [officer_data["name"]] + officer_data.get("variations", [])
        
        for name_variant in names_to_check:
            score = SequenceMatcher(None, officer_name_clean, _normalize_name(name_variant)).ratio()
            if score > best_score and score >= 0.8:  # 80% similarity threshold
                best_score = score
                best_match = officer_data
    
    return best_match

def _normalize_name(name: str) -> str:
    """Normalize name for comparison"""
    if not name:
        return ""
    
    # Remove titles, suffixes, middle initials
    name_clean = re.sub(r'\b(mr|mrs|ms|dr|jr|sr|ii|iii)\b', '', name.lower())
    name_clean = re.sub(r'\b[a-z]\.\s*', '', name_clean)  # Remove middle initials
    name_clean = re.sub(r'[^\w\s]', ' ', name_clean)  # Remove punctuation
    name_clean = re.sub(r'\s+', ' ', name_clean).strip()  # Normalize whitespace
    
    return name_clean

def _calculate_name_match_confidence(search_name: str, matched_name: str) -> float:
    """Calculate confidence in name match"""
    return SequenceMatcher(None, _normalize_name(search_name), _normalize_name(matched_name)).ratio()

def _analyze_officer_risks(officer_data: Dict, current_entity: str) -> List[str]:
    """Analyze risk patterns for an individual officer"""
    risks = []
    
    entities = officer_data.get("entities", [])
    affiliations = officer_data.get("business_affiliations", [])
    
    # Check for serial entity creation
    active_entities = [e for e in entities if e["status"] == "Active"]
    if len(active_entities) >= PROBLEMATIC_OFFICER_PATTERNS["serial_entity_creator"]["threshold"]:
        risks.append(f"serial_entity_creator:{len(active_entities)}")
    
    # Check for regulatory issues
    for affiliation in affiliations:
        for keyword in PROBLEMATIC_OFFICER_PATTERNS["regulatory_issues"]["keywords"]:
            if keyword.lower() in affiliation.lower():
                risks.append(f"regulatory_issues:{keyword}")
                break
    
    # Check for resigned/terminated positions
    resigned_entities = [e for e in entities if e["status"] in ["Resigned", "Terminated"]]
    if len(resigned_entities) >= 2:
        risks.append(f"multiple_resignations:{len(resigned_entities)}")
    
    # Check for offshore connections
    offshore_entities = [e for e in entities if "offshore" in e["entity_name"].lower() or "cayman" in str(e)]
    if offshore_entities:
        risks.append(f"offshore_connections:{len(offshore_entities)}")
    
    # Check for PO Box addresses
    po_box_addresses = [addr for addr in officer_data.get("addresses", []) if "po box" in addr.lower()]
    if po_box_addresses:
        risks.append("po_box_address")
    
    return risks

def _get_officer_risk_flags(officer_data: Dict) -> List[str]:
    """Get human-readable risk flags for an officer"""
    flags = []
    
    entities = officer_data.get("entities", [])
    affiliations = officer_data.get("business_affiliations", [])
    
    # Multiple active entities
    active_entities = [e for e in entities if e["status"] == "Active"]
    if len(active_entities) >= 3:
        flags.append(f"Active in {len(active_entities)} entities simultaneously")
    
    # Recent resignations
    resigned_entities = [e for e in entities if e["status"] in ["Resigned", "Terminated"]]
    if len(resigned_entities) >= 2:
        flags.append(f"Resigned from {len(resigned_entities)} entities")
    
    # License issues
    for affiliation in affiliations:
        if any(word in affiliation.lower() for word in ["suspended", "revoked"]):
            flags.append(f"License issue: {affiliation}")
    
    # Offshore entities
    offshore_entities = [e for e in entities if "offshore" in e["entity_name"].lower()]
    if offshore_entities:
        flags.append(f"Connected to offshore entities")
    
    return flags

def _generate_cross_references(officer_analysis: List[Dict], current_entity: str) -> List[Dict]:
    """Generate cross-reference analysis between officers and entities"""
    cross_refs = []
    
    # Find shared entities among officers
    all_connected_entities = {}
    for officer in officer_analysis:
        for entity in officer["connected_entities"]:
            if entity not in all_connected_entities:
                all_connected_entities[entity] = []
            all_connected_entities[entity].append(officer["name"])
    
    # Create cross-reference entries for shared entities
    for entity_name, officers in all_connected_entities.items():
        if len(officers) > 1:
            cross_refs.append({
                "type": "shared_entity", 
                "entity_name": entity_name,
                "officers": officers,
                "risk_level": "high" if len(officers) >= 3 else "medium"
            })
    
    # Find shared addresses
    address_mapping = {}
    for officer in officer_analysis:
        for address in officer["addresses"]:
            if address not in address_mapping:
                address_mapping[address] = []
            address_mapping[address].append(officer["name"])
    
    for address, officers in address_mapping.items():
        if len(officers) > 1:
            cross_refs.append({
                "type": "shared_address",
                "address": address, 
                "officers": officers,
                "risk_level": "high" if "po box" in address.lower() else "medium"
            })
    
    return cross_refs

def _assess_overall_officer_risks(officer_analysis: List[Dict], cross_references: List[Dict]) -> List[str]:
    """Assess overall risks from officer patterns"""
    risks = []
    
    # Multiple officers with issues
    problematic_officers = [o for o in officer_analysis if o["risk_flags"]]
    if len(problematic_officers) >= 2:
        risks.append(f"multiple_problematic_officers:{len(problematic_officers)}")
    
    # Shared entity patterns
    shared_entities = [cr for cr in cross_references if cr["type"] == "shared_entity"]
    if len(shared_entities) >= 2:
        risks.append(f"complex_entity_web:{len(shared_entities)}")
    
    # Shell company indicators
    shared_addresses = [cr for cr in cross_references if cr["type"] == "shared_address"]
    if shared_addresses:
        risks.append(f"shared_addresses:{len(shared_addresses)}")
    
    return risks

def get_officer_risk_flags(officer_data: Dict) -> List[str]:
    """
    Generate specific red flags based on officer analysis
    
    Args:
        officer_data: Result from analyze_officer_connections()
        
    Returns:
        list: List of red flag strings
    """
    flags = []
    
    officers = officer_data.get("officers", [])
    cross_references = officer_data.get("cross_references", [])
    risk_indicators = officer_data.get("risk_indicators", [])
    
    if not officers:
        return flags
    
    # Officer-specific flags
    for officer in officers:
        officer_name = officer["name"]
        risk_flags = officer.get("risk_flags", [])
        
        for flag in risk_flags:
            flags.append(f"⚠️ Officer {officer_name}: {flag}")
    
    # Cross-reference flags
    for cross_ref in cross_references:
        if cross_ref["type"] == "shared_entity":
            entity_name = cross_ref["entity_name"]
            officer_count = len(cross_ref["officers"])
            flags.append(f"⚠️ {officer_count} officers also connected to {entity_name}")
        
        elif cross_ref["type"] == "shared_address":
            address = cross_ref["address"]
            officer_count = len(cross_ref["officers"])
            flags.append(f"⚠️ {officer_count} officers share address: {address}")
    
    # Pattern flags
    for indicator in risk_indicators:
        if indicator.startswith("serial_entity_creator"):
            count = indicator.split(":")[-1]
            flags.append(f"⚠️ Officer operates {count} active entities simultaneously")
        
        elif indicator.startswith("multiple_problematic_officers"):
            count = indicator.split(":")[-1]
            flags.append(f"⚠️ {count} officers have regulatory or compliance issues")
        
        elif indicator.startswith("complex_entity_web"):
            count = indicator.split(":")[-1]
            flags.append(f"⚠️ Officers connected through {count} shared business entities")
        
        elif indicator.startswith("regulatory_issues"):
            issue_type = indicator.split(":")[-1]
            flags.append(f"⚠️ Officer has {issue_type} regulatory status")
    
    return flags