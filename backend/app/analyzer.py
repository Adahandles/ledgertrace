from .models import (EntityInput, EntityReport, PropertyData, EntityType, CourtData, CourtCase,
                    DomainData, DomainInfo, OfficerData, OfficerInfo, CrossReference, 
                    GrantsData, GrantAward, MonitoringData, Change, Alert, TrendAnalysis,
                    OwnershipData, ShellCompanyReport, OwnershipChainModel, EntityModel, OfficerModel)
from .property_scraper import get_property_info
from .trust_classifier import classify_trust, get_trust_risk_flags, get_trust_source_links
from .court_checker import check_court_cases, get_court_risk_flags
from .domain_analyzer import analyze_domain_presence
from .officer_tracker import analyze_officer_connections  
from .grants_checker import analyze_grants_contracts
from .monitoring_system import check_entity_changes, generate_monitoring_report
from .ownership_tracer import OwnershipTracer
import asyncio
import logging

logger = logging.getLogger(__name__)

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

    # Court case analysis
    court_analysis = check_court_cases(entity.name, entity.county, entity.address)
    
    # Convert court analysis to structured data
    court_cases = []
    if court_analysis.get("cases"):
        for case_data in court_analysis["cases"]:
            court_cases.append(CourtCase(**case_data))
    
    court_data = CourtData(
        cases=court_cases,
        risk_indicators=court_analysis.get("risk_indicators", []),
        case_count=court_analysis.get("case_count", 0),
        has_foreclosure=court_analysis.get("has_foreclosure", False),
        has_tax_lien=court_analysis.get("has_tax_lien", False),
        has_civil=court_analysis.get("has_civil", False),
        has_bankruptcy=court_analysis.get("has_bankruptcy", False)
    )
    
    # Get court-specific risk flags
    court_flags = get_court_risk_flags(court_analysis)
    anomalies.extend(court_flags)
    
    # Add risk score for court issues
    if court_analysis.get("has_foreclosure"):
        risk_score += 25
    if court_analysis.get("has_bankruptcy"):
        risk_score += 30
    if court_analysis.get("has_tax_lien"):
        risk_score += 20
    if court_analysis.get("has_civil"):
        risk_score += 15
    
    # Pattern-based risk increases
    for indicator in court_analysis.get("risk_indicators", []):
        if indicator == "multiple_case_types":
            risk_score += 20
        elif indicator.startswith("recent_court_activity"):
            risk_score += 10
        elif indicator.startswith("high_dollar_cases"):
            risk_score += 15

    # Domain analysis
    domain_analysis = analyze_domain_presence(entity.name)
    
    # Convert domain analysis to structured data
    domain_infos = []
    if domain_analysis.get("domains"):
        for domain_data in domain_analysis["domains"]:
            domain_infos.append(DomainInfo(**domain_data))
    
    domain_data = DomainData(
        domains=domain_infos,
        domain_count=domain_analysis.get("domain_count", 0),
        risk_indicators=domain_analysis.get("risk_indicators", []),
        has_active_website=domain_analysis.get("has_active_website", False),
        has_privacy_protection=domain_analysis.get("has_privacy_protection", False),
        recent_registration=domain_analysis.get("recent_registration", False)
    )
    
    # Add domain risk flags to anomalies
    anomalies.extend(domain_analysis.get("risk_indicators", []))
    
    # Add domain-based risk scoring
    if domain_analysis.get("has_privacy_protection"):
        risk_score += 10
    if domain_analysis.get("recent_registration"):
        risk_score += 15
    if not domain_analysis.get("has_active_website"):
        risk_score += 5

    # Officer cross-reference analysis
    officer_analysis = analyze_officer_connections(entity.name, entity.officers or [])
    
    # Convert officer analysis to structured data
    officer_infos = []
    if officer_analysis.get("officers"):
        for officer_data in officer_analysis["officers"]:
            officer_infos.append(OfficerInfo(**officer_data))
    
    cross_references = []
    if officer_analysis.get("cross_references"):
        for cross_ref in officer_analysis["cross_references"]:
            cross_references.append(CrossReference(**cross_ref))
    
    officer_data = OfficerData(
        officers=officer_infos,
        cross_references=cross_references,
        risk_indicators=officer_analysis.get("risk_indicators", []),
        total_entities_connected=officer_analysis.get("total_entities_connected", 0),
        has_shared_officers=officer_analysis.get("has_shared_officers", False),
        has_problematic_officers=officer_analysis.get("has_problematic_officers", False)
    )
    
    # Add officer risk flags to anomalies
    anomalies.extend(officer_analysis.get("risk_indicators", []))
    
    # Add officer-based risk scoring
    if officer_analysis.get("has_shared_officers"):
        risk_score += 15
    if officer_analysis.get("has_problematic_officers"):
        risk_score += 25
    if officer_analysis.get("total_entities_connected", 0) > 10:
        risk_score += 20

    # Grants and contracts analysis
    grants_analysis = analyze_grants_contracts(entity.name, entity.ein)
    
    # Convert grants analysis to structured data
    grants_list = []
    contracts_list = []
    if grants_analysis.get("grants"):
        for grant_data in grants_analysis["grants"]:
            grants_list.append(GrantAward(**grant_data))
    if grants_analysis.get("contracts"):
        for contract_data in grants_analysis["contracts"]:
            contracts_list.append(GrantAward(**contract_data))
    
    grants_data = GrantsData(
        grants=grants_list,
        contracts=contracts_list,
        total_awards=grants_analysis.get("total_awards", 0),
        active_grants=grants_analysis.get("active_grants", 0),
        active_contracts=grants_analysis.get("active_contracts", 0),
        total_funding=grants_analysis.get("total_funding", 0.0),
        problematic_awards=grants_analysis.get("problematic_awards", 0),
        risk_indicators=grants_analysis.get("risk_indicators", []),
        has_federal_funding=grants_analysis.get("has_federal_funding", False),
        has_state_funding=grants_analysis.get("has_state_funding", False),
        has_compliance_issues=grants_analysis.get("has_compliance_issues", False)
    )
    
    # Add grants risk flags to anomalies
    anomalies.extend(grants_analysis.get("risk_indicators", []))
    
    # Add grants-based risk scoring
    if grants_analysis.get("has_compliance_issues"):
        risk_score += 30
    if grants_analysis.get("problematic_awards", 0) > 0:
        risk_score += 20

    # Monitoring and change detection analysis
    monitoring_analysis = generate_monitoring_report(entity.name)
    
    # Convert monitoring analysis to structured data
    changes_list = []
    alerts_list = []
    trends_list = []
    
    if monitoring_analysis.get("changes"):
        for change_data in monitoring_analysis["changes"]:
            changes_list.append(Change(**change_data))
    
    if monitoring_analysis.get("alerts"):
        for alert_data in monitoring_analysis["alerts"]:
            alerts_list.append(Alert(**alert_data))
    
    if monitoring_analysis.get("trends"):
        for trend_data in monitoring_analysis["trends"]:
            trends_list.append(TrendAnalysis(**trend_data))
    
    monitoring_data = MonitoringData(
        changes_detected=changes_list,
        active_alerts=alerts_list,
        trends=trends_list,
        last_scan=monitoring_analysis.get("last_scan", "2024-01-15T10:00:00Z"),
        scan_frequency=monitoring_analysis.get("scan_frequency", "daily"),
        total_changes=monitoring_analysis.get("total_changes", 0),
        high_risk_changes=monitoring_analysis.get("high_risk_changes", 0),
        active_alert_count=monitoring_analysis.get("active_alert_count", 0),
        monitoring_score=monitoring_analysis.get("monitoring_score", 0)
    )
    
    # Add monitoring-based risk scoring
    risk_score += monitoring_analysis.get("monitoring_score", 0)
    
    # Add monitoring alerts to anomalies
    for alert in alerts_list:
        if alert.severity in ["high", "critical"]:
            anomalies.append(f"🚨 {alert.message}")

    # Ownership chain analysis
    ownership_data = None
    try:
        ownership_report = asyncio.run(analyze_ownership_chains(entity.name))
        if ownership_report:
            ownership_data = convert_ownership_report_to_data(ownership_report)
            
            # Add ownership-based risk scoring
            if ownership_report.get("risk_assessment") == "CRITICAL":
                risk_score += 40
                anomalies.append("🚨 CRITICAL: Complex shell company structure detected")
            elif ownership_report.get("risk_assessment") == "HIGH":
                risk_score += 30
                anomalies.append("⚠️ HIGH: Significant ownership obfuscation detected")
            elif ownership_report.get("risk_assessment") == "MEDIUM":
                risk_score += 20
                anomalies.append("⚠️ MEDIUM: Concerning ownership patterns found")
            
            # Add specific ownership anomalies
            if ownership_report.get("deepest_chain_depth", 0) >= 5:
                anomalies.append("⚠️ Very deep ownership structure (5+ layers)")
            if ownership_report.get("total_shell_indicators", 0) >= 3:
                anomalies.append("⚠️ Multiple shell company indicators detected")
                
    except Exception as e:
        logger.error(f"Ownership analysis failed for {entity.name}: {e}")
        ownership_data = OwnershipData()

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
        court_data=court_data,
        domain_data=domain_data,
        officer_data=officer_data,
        grants_data=grants_data,
        monitoring_data=monitoring_data,
        ownership_data=ownership_data,
        source_links=source_links
    )


async def analyze_ownership_chains(entity_name: str) -> dict:
    """Analyze ownership chains for an entity using OwnershipTracer."""
    try:
        async with OwnershipTracer() as tracer:
            report = await tracer.get_shell_company_report(entity_name)
            return report
    except Exception as e:
        logger.error(f"Ownership analysis error for {entity_name}: {e}")
        return {}


def convert_ownership_report_to_data(ownership_report: dict) -> OwnershipData:
    """Convert ownership tracer report to OwnershipData model."""
    try:
        # Convert ownership chains
        ownership_chains = []
        for chain_data in ownership_report.get("ownership_chains", []):
            # Convert entities in chain
            entities = []
            for entity_data in chain_data.get("entities", []):
                # Convert officers
                officers = []
                for officer_data in entity_data.get("officers", []):
                    officers.append(OfficerModel(
                        name=officer_data.get("name", ""),
                        title=officer_data.get("title", ""),
                        address=officer_data.get("address", "")
                    ))
                
                entities.append(EntityModel(
                    filing_id=entity_data.get("filing_id", ""),
                    name=entity_data.get("name", ""),
                    status=entity_data.get("status", ""),
                    entity_type=entity_data.get("entity_type", ""),
                    date_filed=entity_data.get("date_filed", ""),
                    officers=officers,
                    registered_agent=entity_data.get("registered_agent"),
                    registered_address=entity_data.get("registered_address"),
                    ownership_depth=entity_data.get("ownership_depth", 0),
                    shell_company_score=entity_data.get("shell_company_score", 0.0)
                ))
            
            # Create ownership chain model
            if entities:
                ownership_chain = OwnershipChainModel(
                    chain_id=chain_data.get("chain_id", 0),
                    root_entity=entities[0],
                    chain=entities,
                    depth=chain_data.get("depth", 0),
                    shell_indicators=chain_data.get("shell_indicators", []),
                    risk_score=chain_data.get("risk_score", 0.0),
                    obfuscation_patterns=chain_data.get("obfuscation_patterns", [])
                )
                ownership_chains.append(ownership_chain)
        
        # Extract risk indicators
        risk_indicators = []
        for chain in ownership_chains:
            risk_indicators.extend(chain.shell_indicators)
            risk_indicators.extend(chain.obfuscation_patterns)
        
        # Create shell company report if available
        shell_report = None
        if ownership_report:
            shell_report = ShellCompanyReport(
                entity_name=ownership_report.get("entity_name", ""),
                analysis_date=ownership_report.get("analysis_date", ""),
                risk_assessment=ownership_report.get("risk_assessment", "LOW"),
                shell_company_probability=ownership_report.get("shell_company_probability", 0.0),
                ownership_chains_found=ownership_report.get("ownership_chains_found", 0),
                deepest_chain_depth=ownership_report.get("deepest_chain_depth", 0),
                total_shell_indicators=ownership_report.get("total_shell_indicators", 0),
                total_obfuscation_patterns=ownership_report.get("total_obfuscation_patterns", 0),
                max_risk_score=ownership_report.get("max_risk_score", 0.0),
                avg_risk_score=ownership_report.get("avg_risk_score", 0.0),
                ownership_chains=ownership_chains,
                summary=ownership_report.get("summary", "")
            )
        
        return OwnershipData(
            ownership_analysis=shell_report,
            ownership_chains=ownership_chains,
            shared_officers=[],  # Will be populated by more detailed analysis
            risk_indicators=list(set(risk_indicators)),  # Remove duplicates
            shell_company_score=ownership_report.get("shell_company_probability", 0.0),
            obfuscation_detected=len(ownership_chains) > 0 and any(
                chain.depth >= 3 for chain in ownership_chains
            )
        )
        
    except Exception as e:
        logger.error(f"Error converting ownership report: {e}")
        return OwnershipData()
