"""
Permission Management API Routes.
Endpoints for app permission control and audit logs.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from app.models.schemas import (
    AppPermission, PermissionAudit, PermissionType,
    APIResponse
)
from app.core.ai_firewall import permission_gate

router = APIRouter()


@router.get("/list", response_model=List[AppPermission])
async def list_permissions():
    """
    Get all app permissions.
    Shows which apps have what permissions.
    """
    permissions_list = []
    
    for app_id, perm_data in permission_gate.permissions.items():
        # Convert string permissions to enum
        granted_perms = [
            PermissionType(p) if p in [e.value for e in PermissionType]
            else PermissionType.MOTOR_INTENT
            for p in perm_data['granted']
        ]
        
        permissions_list.append(
            AppPermission(
                app_id=app_id,
                app_name=perm_data['app_name'],
                requested_permissions=granted_perms,
                granted=True,
                timestamp=datetime.now()
            )
        )
    
    return permissions_list


@router.post("/grant", response_model=APIResponse)
async def grant_permission(app_id: str, app_name: str, permission: PermissionType):
    """
    Grant a permission to an application.
    """
    try:
        permission_gate.grant_permission(app_id, app_name, permission.value)
        
        return APIResponse(
            success=True,
            message=f"Granted {permission.value} to {app_name}",
            data={
                "app_id": app_id,
                "app_name": app_name,
                "permission": permission.value
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to grant permission: {str(e)}")


@router.post("/revoke", response_model=APIResponse)
async def revoke_permission(app_id: str, permission: PermissionType):
    """
    Revoke a permission from an application.
    """
    try:
        permission_gate.revoke_permission(app_id, permission.value)
        
        return APIResponse(
            success=True,
            message=f"Revoked {permission.value} from app {app_id}",
            data={
                "app_id": app_id,
                "permission": permission.value
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke permission: {str(e)}")


@router.post("/revoke-all", response_model=APIResponse)
async def revoke_all_permissions(app_id: str):
    """
    Revoke all permissions from an application.
    """
    try:
        if app_id in permission_gate.permissions:
            app_name = permission_gate.permissions[app_id]['app_name']
            # Create a copy of the list to avoid modification issues while iterating
            granted = list(permission_gate.permissions[app_id]['granted'])
            for perm in granted:
                permission_gate.revoke_permission(app_id, perm)
            
            return APIResponse(
                success=True,
                message=f"Revoked all permissions from {app_name}",
                data={"app_id": app_id}
            )
        else:
            return APIResponse(
                success=True,
                message=f"No permissions found for app {app_id}",
                data={"app_id": app_id}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke all permissions: {str(e)}")


@router.get("/audit", response_model=List[PermissionAudit])
async def get_audit_log(limit: int = 50):
    """
    Get permission audit trail.
    Shows all permission grant/revoke events.
    """
    # Get recent audit entries
    recent_logs = permission_gate.audit_log[-limit:]
    
    audit_list = []
    for log in recent_logs:
        # Convert to enum if valid
        perm_type = log['permission']
        if perm_type in [e.value for e in PermissionType]:
            perm_enum = PermissionType(perm_type)
        else:
            perm_enum = PermissionType.MOTOR_INTENT
        
        audit_list.append(
            PermissionAudit(
                app_id=log['app_id'],
                app_name=log['app_name'],
                action=log['action'],
                permission_type=perm_enum,
                timestamp=datetime.fromisoformat(log['timestamp'])
            )
        )
    
    return audit_list


@router.get("/types", response_model=APIResponse)
async def get_permission_types():
    """
    Get information about available permission types.
    Educational endpoint.
    """
    return APIResponse(
        success=True,
        message="Available permission types",
        data={
            "permissions": {
                "motor_intent": {
                    "description": "Basic motor commands (safe)",
                    "risk_level": "low",
                    "data_exposed": ["Beta band (focus)", "Intentional command detection"]
                },
                "focus_level": {
                    "description": "Attention and concentration metrics",
                    "risk_level": "low",
                    "data_exposed": ["Beta/Alpha ratio", "Focus score"]
                },
                "emotional_state": {
                    "description": "Emotional and stress indicators",
                    "risk_level": "medium",
                    "data_exposed": ["Theta band (emotion)", "Alpha band (relaxation)"]
                },
                "full_spectrum": {
                    "description": "Complete neural data (dangerous!)",
                    "risk_level": "critical",
                    "data_exposed": ["All frequency bands", "Raw EEG", "Subconscious data"]
                }
            }
        }
    )


@router.post("/simulate-request", response_model=APIResponse)
async def simulate_app_request(app_id: str, app_name: str, requested: List[PermissionType]):
    """
    Simulate an app requesting permissions (for demo purposes).
    """
    return APIResponse(
        success=True,
        message=f"{app_name} requesting permissions",
        data={
            "app_id": app_id,
            "app_name": app_name,
            "requested_permissions": [p.value for p in requested],
            "recommendation": "Review carefully before granting"
        }
    )
