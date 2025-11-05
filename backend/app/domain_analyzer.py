"""
Domain Analysis Module for LedgerTrace
Provides WHOIS lookup and website verification for entity intelligence
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlparse

# Mock WHOIS database for demonstration
# In production, this would use python-whois or similar library
MOCK_WHOIS_DATA = {
    "sunshinetrustflorida.com": {
        "domain": "sunshinetrustflorida.com",
        "registrar": "GoDaddy.com LLC",
        "creation_date": "2024-01-15",
        "expiration_date": "2025-01-15", 
        "updated_date": "2024-01-15",
        "registrant_name": "John Smith",
        "registrant_email": "jsmith@sunshinetrustflorida.com",
        "registrant_organization": "Sunshine Holdings LLC",
        "registrant_country": "US",
        "name_servers": ["ns1.godaddy.com", "ns2.godaddy.com"],
        "status": ["clientTransferProhibited", "clientUpdateProhibited"],
        "privacy_protection": False
    },
    "offshoretrustinc.com": {
        "domain": "offshoretrustinc.com", 
        "registrar": "Namecheap Inc",
        "creation_date": "2024-10-20",
        "expiration_date": "2025-10-20",
        "updated_date": "2024-10-20", 
        "registrant_name": "Privacy Protection Service",
        "registrant_email": "privacy@whoisprotection.net",
        "registrant_organization": "Privacy Protection Service",
        "registrant_country": "PA",
        "name_servers": ["ns1.namecheap.com", "ns2.namecheap.com"],
        "status": ["clientTransferProhibited"],
        "privacy_protection": True
    },
    "businessinvestmenttrust.org": {
        "domain": "businessinvestmenttrust.org",
        "registrar": "Network Solutions LLC",
        "creation_date": "2024-09-01",
        "expiration_date": "2025-09-01",
        "updated_date": "2024-09-01",
        "registrant_name": "Michael Johnson", 
        "registrant_email": "info@businessinvestmenttrust.org",
        "registrant_organization": "Business Investment Trust LLC",
        "registrant_country": "US",
        "name_servers": ["ns1.networksolutions.com", "ns2.networksolutions.com"],
        "status": ["clientTransferProhibited", "clientUpdateProhibited"],
        "privacy_protection": False
    }
}

# Mock website status data
MOCK_WEBSITE_STATUS = {
    "sunshinetrustflorida.com": {
        "status": "active",
        "ssl_cert": True,
        "content_type": "professional",
        "contact_info": True,
        "privacy_policy": True,
        "terms_of_service": False,
        "social_media_links": ["facebook", "linkedin"],
        "business_address": "123 Investment Blvd, Ocala, FL",
        "phone_number": "(555) 123-4567"
    },
    "offshoretrustinc.com": {
        "status": "parked",
        "ssl_cert": False,
        "content_type": "placeholder", 
        "contact_info": False,
        "privacy_policy": False,
        "terms_of_service": False,
        "social_media_links": [],
        "business_address": None,
        "phone_number": None
    },
    "businessinvestmenttrust.org": {
        "status": "under_construction",
        "ssl_cert": True,
        "content_type": "basic",
        "contact_info": True,
        "privacy_policy": False,
        "terms_of_service": False, 
        "social_media_links": ["linkedin"],
        "business_address": "456 Business Park Dr, Tampa, FL",
        "phone_number": None
    }
}

def analyze_domain_presence(entity_name: str) -> Dict:
    """
    Analyze entity's web presence and domain information
    
    Args:
        entity_name: Name of entity to analyze
        
    Returns:
        dict: Domain analysis results with WHOIS and website data
    """
    if not entity_name:
        return {"domains": [], "risk_indicators": []}
    
    # Generate potential domain variations
    potential_domains = _generate_domain_variations(entity_name)
    
    # Check each potential domain
    found_domains = []
    risk_indicators = []
    
    for domain in potential_domains:
        whois_data = _lookup_whois(domain)
        if whois_data:
            website_data = _check_website_status(domain)
            
            domain_info = {
                "domain": domain,
                "whois": whois_data,
                "website": website_data,
                "match_confidence": _calculate_domain_match_confidence(entity_name, whois_data, website_data)
            }
            found_domains.append(domain_info)
    
    # Analyze risk indicators from domain data
    risk_indicators = _analyze_domain_risks(found_domains, entity_name)
    
    return {
        "domains": found_domains,
        "domain_count": len(found_domains),
        "risk_indicators": risk_indicators,
        "has_active_website": any(d["website"]["status"] == "active" for d in found_domains),
        "has_privacy_protection": any(d["whois"]["privacy_protection"] for d in found_domains),
        "recent_registration": any(_is_recent_registration(d["whois"]["creation_date"]) for d in found_domains)
    }

def _generate_domain_variations(entity_name: str) -> List[str]:
    """Generate potential domain name variations for an entity"""
    variations = []
    
    # Clean entity name
    clean_name = re.sub(r'[^\w\s]', '', entity_name.lower())
    clean_name = re.sub(r'\s+', '', clean_name)
    
    # Remove common business suffixes
    suffixes_to_remove = ['llc', 'inc', 'corp', 'trust', 'foundation', 'ltd', 'company', 'co']
    for suffix in suffixes_to_remove:
        clean_name = clean_name.replace(suffix, '')
    
    # Generate common domain patterns
    base_variations = [
        clean_name,
        clean_name.replace(' ', ''),
        clean_name.replace(' ', '-'),
        clean_name + 'llc',
        clean_name + 'trust',
        clean_name + 'inc'
    ]
    
    # Add common TLDs
    tlds = ['.com', '.org', '.net', '.us']
    
    for base in base_variations:
        if base and len(base) > 2:  # Avoid very short domains
            for tld in tlds:
                variations.append(base + tld)
    
    # Add some entity-specific patterns based on mock data
    entity_lower = entity_name.lower()
    if 'sunshine' in entity_lower and 'holdings' in entity_lower:
        variations.append('sunshinetrustflorida.com')
    elif 'offshore' in entity_lower and 'trust' in entity_lower:
        variations.append('offshoretrustinc.com')
    elif 'business' in entity_lower and 'investment' in entity_lower:
        variations.append('businessinvestmenttrust.org')
    
    return list(set(variations))  # Remove duplicates

def _lookup_whois(domain: str) -> Optional[Dict]:
    """Mock WHOIS lookup - in production would use actual WHOIS service"""
    return MOCK_WHOIS_DATA.get(domain)

def _check_website_status(domain: str) -> Dict:
    """Mock website status check - in production would make HTTP requests"""
    return MOCK_WEBSITE_STATUS.get(domain, {
        "status": "not_found",
        "ssl_cert": False,
        "content_type": "none",
        "contact_info": False,
        "privacy_policy": False,
        "terms_of_service": False,
        "social_media_links": [],
        "business_address": None,
        "phone_number": None
    })

def _calculate_domain_match_confidence(entity_name: str, whois_data: Dict, website_data: Dict) -> float:
    """Calculate confidence that domain belongs to the entity"""
    confidence = 0.0
    
    entity_lower = entity_name.lower()
    
    # Check registrant organization match
    reg_org = whois_data.get("registrant_organization", "").lower()
    if reg_org and reg_org in entity_lower:
        confidence += 0.4
    
    # Check registrant name relevance
    reg_name = whois_data.get("registrant_name", "").lower()
    if reg_name and not reg_name.startswith("privacy"):
        confidence += 0.2
    
    # Check website contact info
    if website_data.get("contact_info"):
        confidence += 0.2
    
    # Check business address
    if website_data.get("business_address"):
        confidence += 0.15
    
    # Penalty for privacy protection (suspicious)
    if whois_data.get("privacy_protection"):
        confidence -= 0.1
    
    # Penalty for parked/placeholder sites
    if website_data.get("status") in ["parked", "placeholder"]:
        confidence -= 0.2
    
    return max(0.0, min(1.0, confidence))

def _is_recent_registration(creation_date_str: str) -> bool:
    """Check if domain was registered recently (within 90 days)"""
    try:
        creation_date = datetime.strptime(creation_date_str, "%Y-%m-%d")
        cutoff_date = datetime.now() - timedelta(days=90)
        return creation_date >= cutoff_date
    except (ValueError, TypeError):
        return False

def _analyze_domain_risks(domains: List[Dict], entity_name: str) -> List[str]:
    """Analyze domains for risk indicators"""
    indicators = []
    
    if not domains:
        indicators.append("no_web_presence")
        return indicators
    
    # Check for privacy protection
    privacy_domains = [d for d in domains if d["whois"].get("privacy_protection")]
    if privacy_domains:
        indicators.append(f"privacy_protection:{len(privacy_domains)}")
    
    # Check for recent registrations
    recent_domains = [d for d in domains if _is_recent_registration(d["whois"].get("creation_date", ""))]
    if recent_domains:
        indicators.append(f"recent_registration:{len(recent_domains)}")
    
    # Check for parked/inactive sites
    inactive_domains = [d for d in domains if d["website"].get("status") in ["parked", "under_construction", "not_found"]]
    if inactive_domains:
        indicators.append(f"inactive_websites:{len(inactive_domains)}")
    
    # Check for missing contact information
    no_contact_domains = [d for d in domains if not d["website"].get("contact_info")]
    if no_contact_domains and len(no_contact_domains) == len(domains):
        indicators.append("no_contact_info")
    
    # Check for suspicious registrant countries
    foreign_domains = [d for d in domains if d["whois"].get("registrant_country") not in ["US", "CA"]]
    if foreign_domains:
        indicators.append(f"foreign_registration:{len(foreign_domains)}")
    
    # Check domain-entity name mismatch
    low_confidence_domains = [d for d in domains if d.get("match_confidence", 0) < 0.5]
    if low_confidence_domains:
        indicators.append(f"low_confidence_match:{len(low_confidence_domains)}")
    
    return indicators

def get_domain_risk_flags(domain_data: Dict) -> List[str]:
    """
    Generate specific red flags based on domain analysis
    
    Args:
        domain_data: Result from analyze_domain_presence()
        
    Returns:
        list: List of red flag strings  
    """
    flags = []
    
    domains = domain_data.get("domains", [])
    risk_indicators = domain_data.get("risk_indicators", [])
    
    # No web presence
    if not domains:
        flags.append("⚠️ Entity has no detectable web presence or domain registration")
        return flags
    
    # Privacy protection flags
    for indicator in risk_indicators:
        if indicator.startswith("privacy_protection"):
            count = indicator.split(":")[-1]
            flags.append(f"⚠️ Entity uses privacy protection on {count} domain(s)")
        
        elif indicator.startswith("recent_registration"):
            count = indicator.split(":")[-1] 
            flags.append(f"⚠️ Entity registered {count} domain(s) within last 90 days")
        
        elif indicator.startswith("inactive_websites"):
            count = indicator.split(":")[-1]
            flags.append(f"⚠️ Entity has {count} parked or inactive website(s)")
        
        elif indicator == "no_contact_info":
            flags.append("⚠️ Entity websites lack contact information")
        
        elif indicator.startswith("foreign_registration"):
            count = indicator.split(":")[-1]
            flags.append(f"⚠️ Entity has {count} domain(s) registered outside US/Canada")
        
        elif indicator.startswith("low_confidence_match"):
            count = indicator.split(":")[-1]
            flags.append(f"⚠️ {count} domain(s) may not belong to this entity")
    
    # Specific pattern flags
    suspicious_patterns = []
    for domain_info in domains:
        domain = domain_info["domain"]
        whois = domain_info["whois"]
        website = domain_info["website"]
        
        # Recently registered before getting funds
        if (_is_recent_registration(whois.get("creation_date", "")) and 
            website.get("status") in ["under_construction", "basic"]):
            suspicious_patterns.append(f"Domain {domain} registered recently with minimal website")
    
    if suspicious_patterns:
        flags.extend([f"⚠️ {pattern}" for pattern in suspicious_patterns])
    
    return flags