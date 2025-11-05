from .models import EntityInput, EntityReport, PropertyData, EntityType
from .property_scraper import get_property_info
from .trust_classifier import classify_trust, get_trust_risk_flags, get_trust_source_links

def analyze_entity(entity: EntityInput) -> EntityReport:
    anomalies = []
    risk_score = 0
    property_data = None

    # Trust classification analysis
    trust_classification = classify_trust(entity.name)
    entity_type = EntityType(**trust_classification)
    
    # Get trust-specific risk flags
    trust_flags = get_trust_risk_flags(trust_classification, has_ein=entity.ein is not None)
    anomalies.extend(trust_flags)
    
    # Add risk score for trust-specific issues
    if trust_classification["high_risk"]:
        risk_score += 30
    if trust_classification["requires_regulation"] and entity.ein is None:
        risk_score += 25

    # Entity-level risk analysis
    if entity.ein is None:
        anomalies.append("⚠️ No EIN provided.")
        risk_score += 20

    if len(entity.officers or []) > 5:
        anomalies.append("⚠️ More than 5 officers listed.")
        risk_score += 10

    # Property-level risk analysis
    if entity.address:
        # Get property information
        prop_info = get_property_info(entity.address, entity.county)
        
        if prop_info:
            property_data = PropertyData(**prop_info)
            
            # Property-based risk rules
            if "PO Box" in entity.address or "P.O. Box" in entity.address:
                anomalies.append("⚠️ PO Box detected in address.")
                risk_score += 15
                
            if prop_info.get("delinquent_taxes"):
                anomalies.append("⚠️ Delinquent property taxes detected.")
                risk_score += 20
                
            land_use = prop_info.get("land_use", "").lower()
            if "vacant" in land_use:
                anomalies.append("⚠️ Property appears vacant or undeveloped.")
                risk_score += 15
                
            if "mail" in land_use or "mail drop" in land_use:
                anomalies.append("⚠️ Property address may be a mail drop service.")
                risk_score += 25
                
            # Additional property risk indicators
            if property_data.market_value == "N/A" or property_data.market_value == "$0":
                anomalies.append("⚠️ Property has no assessed market value.")
                risk_score += 10

    # Generate source links based on entity type
    source_links = get_trust_source_links(entity.name, trust_classification)
    
    # Add standard source links
    encoded_name = entity.name.replace(" ", "%20")
    source_links.update({
        "sunbiz": f"http://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults?InquiryType=EntityName&SearchTerm={encoded_name}",
        "irs": f"https://apps.irs.gov/app/eos/allSearch?names={encoded_name}",
        "sba": f"https://www.sba.gov/partners/contracting-officials/procurement-center-representatives/search?name={encoded_name}"
    })

    return EntityReport(
        name=entity.name,
        risk_score=min(risk_score, 100),  # Cap at 100
        anomalies=anomalies,
        entity_type=entity_type,
        property=property_data,
        source_links=source_links
    )
