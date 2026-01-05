"""
Threat Detection API Routes.
Endpoints for monitoring security threats.
"""

from fastapi import APIRouter
from typing import List
from datetime import datetime, timedelta

from app.models.schemas import ThreatAlert, ThreatLevel, APIResponse
from app.core.ai_firewall import threat_detector

router = APIRouter()


@router.get("/recent", response_model=List[ThreatAlert])
async def get_recent_threats(limit: int = 20):
    """
    Get recent threat detections.
    """
    recent = threat_detector.threat_log[-limit:]
    
    threat_list = []
    for threat in recent:
        threat_list.append(
            ThreatAlert(
                threat_id=threat['threat_id'],
                threat_type=threat['threat_type'],
                level=ThreatLevel(threat['level']),
                description=threat['description'],
                app_id=threat.get('app_id'),
                timestamp=datetime.fromisoformat(threat['timestamp']),
                mitigated=threat['mitigated']
            )
        )
    
    return threat_list


@router.get("/stats", response_model=APIResponse)
async def get_threat_statistics():
    """
    Get aggregated threat statistics.
    """
    total_threats = len(threat_detector.threat_log)
    
    # Count by level
    level_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    type_counts = {}
    
    for threat in threat_detector.threat_log:
        level_counts[threat['level']] += 1
        threat_type = threat['threat_type']
        type_counts[threat_type] = type_counts.get(threat_type, 0) + 1
    
    # Recent threats (last 24 hours)
    recent_24h = [
        t for t in threat_detector.threat_log
        if datetime.fromisoformat(t['timestamp']) > datetime.now() - timedelta(hours=24)
    ]
    
    return APIResponse(
        success=True,
        message="Threat statistics",
        data={
            "total_threats": total_threats,
            "threats_24h": len(recent_24h),
            "by_level": level_counts,
            "by_type": type_counts,
            "most_common_threat": max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "None"
        }
    )


@router.get("/types", response_model=APIResponse)
async def get_threat_types():
    """
    Get information about threat types.
    Educational endpoint.
    """
    return APIResponse(
        success=True,
        message="Known threat types",
        data={
            "threats": {
                "excessive_permissions": {
                    "description": "App requesting more data than needed",
                    "severity": "high",
                    "mitigation": "Deny full_spectrum permission, grant minimal access"
                },
                "data_harvesting": {
                    "description": "Unusually high request frequency",
                    "severity": "medium",
                    "mitigation": "Rate limiting, suspicious app flagging"
                },
                "emotional_surveillance": {
                    "description": "Accessing emotional data without justification",
                    "severity": "critical",
                    "mitigation": "Block emotional_state permission, alert user"
                },
                "brain_jacking": {
                    "description": "Attempting to inject malicious neural patterns",
                    "severity": "critical",
                    "mitigation": "Immediate connection termination, quarantine app"
                }
            }
        }
    )


@router.post("/simulate", response_model=APIResponse)
async def simulate_threat(threat_type: str, app_id: str = "demo_app"):
    """
    Simulate a threat detection (for demo purposes).
    """
    # Detect the simulated threat
    threats = threat_detector.detect_threats(
        app_id=app_id,
        requested_permissions=['full_spectrum'],
        request_frequency=15
    )
    
    return APIResponse(
        success=True,
        message=f"Simulated {len(threats)} threats",
        data={
            "threats": [
                {
                    "type": t['threat_type'],
                    "level": t['level'],
                    "description": t['description']
                }
                for t in threats
            ]
        }
    )
