"""
Monitoring and Alerts System for LedgerTrace
Automated tracking and change detection for entities
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict

@dataclass
class EntitySnapshot:
    """Snapshot of entity data at a point in time"""
    entity_name: str
    timestamp: str
    risk_score: int
    anomalies: List[str]
    trust_classification: Dict
    court_cases: List[Dict]
    officer_data: Dict
    domain_data: Dict
    grants_data: Dict
    checksum: str

@dataclass  
class ChangeAlert:
    """Alert for detected changes in entity data"""
    entity_name: str
    alert_type: str
    severity: str  # low, medium, high, critical
    description: str
    old_value: str
    new_value: str
    timestamp: str
    requires_investigation: bool = False

# Mock entity monitoring database
# In production, this would be a proper database with change tracking
MOCK_MONITORING_DB = {
    "tracked_entities": {
        "sunshine_holdings_llc": {
            "entity_name": "Sunshine Holdings LLC",
            "monitoring_start": "2024-10-01",
            "alert_frequency": "daily",
            "watch_reasons": ["active_foreclosure", "recent_funding"],
            "last_check": "2024-11-04",
            "total_alerts": 3
        },
        "business_investment_trust_llc": {
            "entity_name": "Business Investment Trust LLC", 
            "monitoring_start": "2024-09-15",
            "alert_frequency": "immediate",
            "watch_reasons": ["compliance_violations", "dbpr_action"],
            "last_check": "2024-11-04",
            "total_alerts": 7
        }
    },
    "entity_snapshots": {
        "sunshine_holdings_llc": [
            {
                "timestamp": "2024-11-01T10:00:00Z",
                "risk_score": 35,
                "anomalies": ["⚠️ No EIN provided."],
                "court_cases_count": 0,
                "grants_total": 0
            },
            {
                "timestamp": "2024-11-04T10:00:00Z", 
                "risk_score": 60,
                "anomalies": ["⚠️ No EIN provided.", "⚠️ Entity involved in 1 active foreclosure case(s)"],
                "court_cases_count": 1,
                "grants_total": 2950000  # $2.95M in new grants
            }
        ]
    },
    "alert_history": [
        {
            "entity_name": "Sunshine Holdings LLC",
            "alert_type": "court_case_filed",
            "severity": "high",
            "description": "New foreclosure case filed: 2024-CA-001234",
            "timestamp": "2024-11-04T08:30:00Z"
        },
        {
            "entity_name": "Sunshine Holdings LLC", 
            "alert_type": "funding_received",
            "severity": "medium",
            "description": "Received $2.5M FEMA grant while in foreclosure",
            "timestamp": "2024-11-04T12:15:00Z"
        },
        {
            "entity_name": "Business Investment Trust LLC",
            "alert_type": "compliance_violation",
            "severity": "critical",
            "description": "Grant marked non-compliant - misuse investigation", 
            "timestamp": "2024-10-20T14:45:00Z"
        }
    ]
}

# Alert configuration
ALERT_RULES = {
    "risk_score_increase": {
        "threshold": 15,
        "severity": "medium",
        "description": "Risk score increased by {change} points"
    },
    "new_court_case": {
        "severity": "high", 
        "description": "New court case filed: {case_type}"
    },
    "funding_while_litigation": {
        "severity": "critical",
        "description": "Received funding while involved in court case"
    },
    "officer_change": {
        "severity": "medium",
        "description": "Officer roster change detected"
    },
    "compliance_violation": {
        "severity": "critical", 
        "description": "New compliance violation or investigation"
    },
    "domain_registration": {
        "severity": "low",
        "description": "New domain registration detected"
    }
}

def add_entity_to_monitoring(entity_name: str, watch_reasons: List[str] = None, 
                           alert_frequency: str = "daily") -> Dict:
    """
    Add entity to monitoring system
    
    Args:
        entity_name: Entity to monitor
        watch_reasons: Reasons for monitoring (optional)
        alert_frequency: How often to check (immediate, daily, weekly)
        
    Returns:
        dict: Monitoring setup confirmation
    """
    entity_key = _normalize_entity_key(entity_name)
    
    monitoring_config = {
        "entity_name": entity_name,
        "monitoring_start": datetime.now().isoformat()[:10],
        "alert_frequency": alert_frequency,
        "watch_reasons": watch_reasons or [],
        "last_check": None,
        "total_alerts": 0,
        "status": "active"
    }
    
    # In production, would save to database
    MOCK_MONITORING_DB["tracked_entities"][entity_key] = monitoring_config
    
    return {
        "success": True,
        "message": f"Entity {entity_name} added to monitoring",
        "monitoring_id": entity_key,
        "config": monitoring_config
    }

def check_entity_changes(entity_name: str, current_data: Dict, 
                        previous_snapshot: Optional[Dict] = None) -> List[ChangeAlert]:
    """
    Check for changes in entity data and generate alerts
    
    Args:
        entity_name: Entity being checked
        current_data: Current entity analysis data
        previous_snapshot: Previous snapshot for comparison
        
    Returns:
        list: List of change alerts
    """
    alerts = []
    
    if not previous_snapshot:
        # No previous data, just record current state
        return alerts
    
    # Check risk score changes
    old_risk = previous_snapshot.get("risk_score", 0)
    new_risk = current_data.get("risk_score", 0) 
    risk_change = new_risk - old_risk
    
    if abs(risk_change) >= ALERT_RULES["risk_score_increase"]["threshold"]:
        alert = ChangeAlert(
            entity_name=entity_name,
            alert_type="risk_score_change",
            severity=ALERT_RULES["risk_score_increase"]["severity"],
            description=ALERT_RULES["risk_score_increase"]["description"].format(change=abs(risk_change)),
            old_value=str(old_risk),
            new_value=str(new_risk),
            timestamp=datetime.now().isoformat(),
            requires_investigation=risk_change > 25
        )
        alerts.append(alert)
    
    # Check for new court cases
    old_court_count = previous_snapshot.get("court_cases_count", 0)
    new_court_count = len(current_data.get("court_data", {}).get("cases", []))
    
    if new_court_count > old_court_count:
        # Find new cases
        court_cases = current_data.get("court_data", {}).get("cases", [])
        if court_cases:
            latest_case = court_cases[-1]  # Assume newest case is last
            alert = ChangeAlert(
                entity_name=entity_name,
                alert_type="new_court_case",
                severity=ALERT_RULES["new_court_case"]["severity"],
                description=ALERT_RULES["new_court_case"]["description"].format(
                    case_type=latest_case.get("case_type", "Unknown")
                ),
                old_value=str(old_court_count),
                new_value=str(new_court_count),
                timestamp=datetime.now().isoformat(),
                requires_investigation=latest_case.get("case_type") in ["Foreclosure", "Bankruptcy"]
            )
            alerts.append(alert)
    
    # Check for funding while in litigation  
    has_court_cases = new_court_count > 0
    grants_data = current_data.get("grants_data", {})
    recent_funding = _has_recent_funding(grants_data)
    
    if has_court_cases and recent_funding:
        alert = ChangeAlert(
            entity_name=entity_name,
            alert_type="funding_while_litigation",
            severity=ALERT_RULES["funding_while_litigation"]["severity"],
            description=ALERT_RULES["funding_while_litigation"]["description"],
            old_value="no_concurrent_issues",
            new_value="funding_and_litigation",
            timestamp=datetime.now().isoformat(),
            requires_investigation=True
        )
        alerts.append(alert)
    
    # Check for compliance violations
    grants_compliance = grants_data.get("has_compliance_issues", False)
    old_compliance_issues = previous_snapshot.get("compliance_issues", False)
    
    if grants_compliance and not old_compliance_issues:
        alert = ChangeAlert(
            entity_name=entity_name,
            alert_type="compliance_violation",
            severity=ALERT_RULES["compliance_violation"]["severity"],
            description=ALERT_RULES["compliance_violation"]["description"],
            old_value="compliant",
            new_value="violation_detected", 
            timestamp=datetime.now().isoformat(),
            requires_investigation=True
        )
        alerts.append(alert)
    
    # Check officer changes
    current_officers = set(current_data.get("officers", []))
    previous_officers = set(previous_snapshot.get("officers", []))
    
    if current_officers != previous_officers:
        alert = ChangeAlert(
            entity_name=entity_name,
            alert_type="officer_change",
            severity=ALERT_RULES["officer_change"]["severity"],
            description=ALERT_RULES["officer_change"]["description"],
            old_value=str(sorted(previous_officers)),
            new_value=str(sorted(current_officers)),
            timestamp=datetime.now().isoformat(),
            requires_investigation=len(current_officers) < len(previous_officers)  # Officers leaving
        )
        alerts.append(alert)
    
    return alerts

def generate_monitoring_report(entity_name: str, days_back: int = 30) -> Dict:
    """
    Generate monitoring report for an entity
    
    Args:
        entity_name: Entity to report on
        days_back: Number of days to look back
        
    Returns:
        dict: Comprehensive monitoring report
    """
    entity_key = _normalize_entity_key(entity_name)
    
    # Get monitoring configuration
    monitoring_config = MOCK_MONITORING_DB["tracked_entities"].get(entity_key, {})
    
    if not monitoring_config:
        return {
            "error": f"Entity {entity_name} is not being monitored",
            "suggestion": "Add entity to monitoring system first"
        }
    
    # Get alert history
    cutoff_date = datetime.now() - timedelta(days=days_back)
    recent_alerts = []
    
    for alert in MOCK_MONITORING_DB["alert_history"]:
        alert_date = datetime.fromisoformat(alert["timestamp"].replace("Z", "+00:00"))
        if (alert["entity_name"] == entity_name and 
            alert_date >= cutoff_date):
            recent_alerts.append(alert)
    
    # Get snapshots for trend analysis
    snapshots = MOCK_MONITORING_DB["entity_snapshots"].get(entity_key, [])
    
    # Calculate trends
    trends = _calculate_trends(snapshots)
    
    # Generate risk assessment
    risk_assessment = _assess_monitoring_risk(recent_alerts, trends, monitoring_config)
    
    return {
        "entity_name": entity_name,
        "monitoring_config": monitoring_config,
        "report_period": f"{days_back} days",
        "alert_summary": {
            "total_alerts": len(recent_alerts),
            "critical_alerts": len([a for a in recent_alerts if a["severity"] == "critical"]),
            "high_alerts": len([a for a in recent_alerts if a["severity"] == "high"]),
            "medium_alerts": len([a for a in recent_alerts if a["severity"] == "medium"])
        },
        "recent_alerts": recent_alerts,
        "trends": trends,
        "risk_assessment": risk_assessment,
        "recommendations": _generate_recommendations(recent_alerts, trends)
    }

def _normalize_entity_key(entity_name: str) -> str:
    """Normalize entity name for use as database key"""
    return entity_name.lower().replace(" ", "_").replace(".", "").replace(",", "")

def _has_recent_funding(grants_data: Dict, days_back: int = 90) -> bool:
    """Check if entity received funding recently"""
    if not grants_data:
        return False
    
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    for award in grants_data.get("grants", []) + grants_data.get("contracts", []):
        try:
            award_date = datetime.strptime(award.get("award_date", ""), "%Y-%m-%d")
            if award_date >= cutoff_date:
                return True
        except ValueError:
            continue
    
    return False

def _calculate_trends(snapshots: List[Dict]) -> Dict:
    """Calculate trends from historical snapshots"""
    if len(snapshots) < 2:
        return {"insufficient_data": True}
    
    # Sort by timestamp
    sorted_snapshots = sorted(snapshots, key=lambda x: x["timestamp"])
    
    # Calculate risk score trend
    risk_scores = [s["risk_score"] for s in sorted_snapshots]
    risk_trend = "increasing" if risk_scores[-1] > risk_scores[0] else "decreasing" if risk_scores[-1] < risk_scores[0] else "stable"
    
    # Calculate alert frequency trend
    alert_counts = [len(s.get("anomalies", [])) for s in sorted_snapshots]
    alert_trend = "increasing" if alert_counts[-1] > alert_counts[0] else "decreasing" if alert_counts[-1] < alert_counts[0] else "stable"
    
    return {
        "risk_score_trend": risk_trend,
        "risk_score_change": risk_scores[-1] - risk_scores[0],
        "alert_frequency_trend": alert_trend,
        "total_snapshots": len(snapshots),
        "monitoring_duration_days": len(snapshots)  # Simplified calculation
    }

def _assess_monitoring_risk(alerts: List[Dict], trends: Dict, config: Dict) -> Dict:
    """Assess overall risk based on monitoring data"""
    risk_level = "low"
    concerns = []
    
    # Critical alerts automatically elevate risk
    critical_alerts = [a for a in alerts if a["severity"] == "critical"]
    if critical_alerts:
        risk_level = "critical"
        concerns.append(f"{len(critical_alerts)} critical alert(s) detected")
    
    # Multiple high alerts
    high_alerts = [a for a in alerts if a["severity"] == "high"]
    if len(high_alerts) >= 3:
        risk_level = "high" if risk_level == "low" else risk_level
        concerns.append(f"{len(high_alerts)} high-priority alerts")
    
    # Negative trends
    if trends.get("risk_score_trend") == "increasing":
        risk_change = trends.get("risk_score_change", 0)
        if risk_change > 20:
            risk_level = "high" if risk_level == "low" else risk_level
            concerns.append(f"Risk score increased by {risk_change} points")
    
    # Patterns indicating deterioration
    alert_types = [a["alert_type"] for a in alerts]
    if "compliance_violation" in alert_types and "funding_while_litigation" in alert_types:
        risk_level = "critical"
        concerns.append("Pattern indicates potential fraud or misuse")
    
    return {
        "risk_level": risk_level,
        "concerns": concerns,
        "confidence": "high" if len(alerts) > 0 else "medium"
    }

def _generate_recommendations(alerts: List[Dict], trends: Dict) -> List[str]:
    """Generate recommendations based on monitoring data"""
    recommendations = []
    
    # Critical alert recommendations
    critical_alerts = [a for a in alerts if a["severity"] == "critical"]
    if critical_alerts:
        recommendations.append("Immediate investigation required for critical compliance violations")
        recommendations.append("Consider suspending any active funding pending investigation")
    
    # Court case recommendations  
    court_alerts = [a for a in alerts if a["alert_type"] == "new_court_case"]
    if court_alerts:
        recommendations.append("Monitor court case proceedings for potential impact on entity stability")
        recommendations.append("Review any active contracts or grants for performance risk")
    
    # Trend-based recommendations
    if trends.get("risk_score_trend") == "increasing":
        recommendations.append("Increase monitoring frequency due to deteriorating risk profile")
    
    # Funding recommendations
    funding_alerts = [a for a in alerts if "funding" in a["alert_type"]]
    if funding_alerts:
        recommendations.append("Enhanced oversight recommended for all funding disbursements")
        recommendations.append("Require additional reporting or site visits")
    
    if not recommendations:
        recommendations.append("Continue standard monitoring procedures")
        recommendations.append("No immediate action required based on current data")
    
    return recommendations