"""
Pydantic models for API request/response validation.
Defines the data structures for the Neuro-Privacy Guard API.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# EEG Signal Models
# ============================================================================

class EEGSignalInput(BaseModel):
    """Raw EEG signal input from BCI device or synthetic generator."""
    
    channels: Dict[str, List[float]] = Field(
        ..., 
        description="Multi-channel EEG data, e.g., {'C3': [0.1, 0.2, ...], 'C4': [...]}"
    )
    sampling_rate: int = Field(256, description="Sampling rate in Hz")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    
    @validator('channels')
    def validate_channels(cls, v):
        """Ensure all channels have data."""
        if not v:
            raise ValueError("At least one channel required")
        return v


class FrequencyBands(BaseModel):
    """Extracted frequency band powers from EEG signal."""
    
    delta: float = Field(..., description="Delta band (0.5-4 Hz) power")
    theta: float = Field(..., description="Theta band (4-8 Hz) power")
    alpha: float = Field(..., description="Alpha band (8-13 Hz) power")
    beta: float = Field(..., description="Beta band (13-30 Hz) power")
    gamma: float = Field(..., description="Gamma band (30-100 Hz) power")


# ============================================================================
# Intent Classification Models
# ============================================================================

class IntentType(str, Enum):
    """Types of neural intent."""
    INTENTIONAL = "intentional"
    SUBCONSCIOUS = "subconscious"
    NEUTRAL = "neutral"


class IntentClassification(BaseModel):
    """Result of intent classification."""
    
    intent_type: IntentType
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    explanation: str = Field("", description="Human-readable explanation")


# ============================================================================
# Privacy Models
# ============================================================================

class PrivacyLevel(BaseModel):
    """User privacy level setting."""
    
    level: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Privacy level: 0.0=max privacy (more noise), 1.0=max utility"
    )


class PrivacyStatus(BaseModel):
    """Current privacy configuration."""
    
    current_level: float
    epsilon: float
    delta: float
    noise_applied: bool


# ============================================================================
# Permission Models
# ============================================================================

class PermissionType(str, Enum):
    """Types of neural data permissions."""
    MOTOR_INTENT = "motor_intent"
    FOCUS_LEVEL = "focus_level"
    EMOTIONAL_STATE = "emotional_state"
    FULL_SPECTRUM = "full_spectrum"


class AppPermission(BaseModel):
    """Permission request from an application."""
    
    app_id: str
    app_name: str
    requested_permissions: List[PermissionType]
    granted: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class PermissionAudit(BaseModel):
    """Audit log entry for permission events."""
    
    app_id: str
    app_name: str
    action: Literal["grant", "revoke", "request"]
    permission_type: PermissionType
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Threat Detection Models
# ============================================================================

class ThreatLevel(str, Enum):
    """Severity levels for threats."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatAlert(BaseModel):
    """Threat detection alert."""
    
    threat_id: str
    threat_type: str
    level: ThreatLevel
    description: str
    app_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    mitigated: bool = False


# ============================================================================
# Processing Pipeline Models
# ============================================================================

class SignalProcessingResult(BaseModel):
    """Complete result from signal processing pipeline."""
    
    original_channels: int
    sampling_rate: int
    frequency_bands: FrequencyBands
    intent_classification: IntentClassification
    privacy_applied: bool
    threats_detected: List[ThreatAlert] = []
    timestamp: datetime = Field(default_factory=datetime.now)


class SyntheticEEGRequest(BaseModel):
    """Request to generate synthetic EEG data."""
    
    brain_state: Literal["focused", "relaxed", "stressed", "neutral"] = "neutral"
    duration: float = Field(2.0, ge=0.5, le=10.0, description="Duration in seconds")
    num_channels: int = Field(8, ge=1, le=32)
    sampling_rate: int = Field(256, ge=128, le=1024)


# ============================================================================
# API Response Models
# ============================================================================

class APIResponse(BaseModel):
    """Standard API response wrapper."""
    
    success: bool
    message: str
    data: Optional[Dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthCheck(BaseModel):
    """Health check response."""
    
    status: str = "healthy"
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
