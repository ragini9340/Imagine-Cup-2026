"""
Privacy Control API Routes.
Endpoints for managing user privacy settings.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import PrivacyLevel, PrivacyStatus, APIResponse
from app.config import settings

router = APIRouter()

# Global privacy state (in production, use database)
current_privacy_state = {
    "level": settings.DEFAULT_PRIVACY_LEVEL,
    "epsilon": settings.DEFAULT_EPSILON,
    "delta": settings.DEFAULT_DELTA
}


@router.post("/set-level", response_model=APIResponse)
async def set_privacy_level(privacy: PrivacyLevel):
    """
    Update user's privacy level.
    
    - 0.0 = Maximum privacy (more noise, less utility)
    - 1.0 = Maximum utility (less noise, more data exposure)
    """
    try:
        current_privacy_state["level"] = privacy.level
        
        # Adjust epsilon based on level
        # Higher level = higher epsilon = less noise
        current_privacy_state["epsilon"] = settings.DEFAULT_EPSILON * (privacy.level + 0.1)
        
        return APIResponse(
            success=True,
            message=f"Privacy level updated to {privacy.level:.2f}",
            data=current_privacy_state
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update privacy: {str(e)}")


@router.get("/status", response_model=PrivacyStatus)
async def get_privacy_status():
    """Get current privacy configuration."""
    return PrivacyStatus(
        current_level=current_privacy_state["level"],
        epsilon=current_privacy_state["epsilon"],
        delta=current_privacy_state["delta"],
        noise_applied=True
    )


@router.get("/info", response_model=APIResponse)
async def get_privacy_info():
    """
    Get information about privacy mechanisms.
    Educational endpoint.
    """
    return APIResponse(
        success=True,
        message="Privacy protection information",
        data={
            "mechanism": "Differential Privacy (Laplacian Noise)",
            "current_level": current_privacy_state["level"],
            "levels": {
                "0.0-0.3": "Maximum Privacy - Heavy noise, strong protection, reduced utility",
                "0.4-0.6": "Balanced - Moderate noise, good protection, decent utility",
                "0.7-1.0": "Maximum Utility - Light noise, basic protection, high utility"
            },
            "parameters": {
                "epsilon": {
                    "current": current_privacy_state["epsilon"],
                    "description": "Privacy budget - lower means more privacy"
                },
                "delta": {
                    "current": current_privacy_state["delta"],
                    "description": "Probability of privacy breach"
                }
            },
            "what_is_protected": [
                "Individual brain signatures (fingerprinting prevention)",
                "Subconscious emotional states",
                "Memory and cognitive patterns",
                "Sensitive frequency band data"
            ]
        }
    )
