"""
Signal Processing API Routes.
Endpoints for EEG signal ingestion and processing.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
from datetime import datetime

from app.models.schemas import (
    EEGSignalInput, SyntheticEEGRequest,
    SignalProcessingResult, FrequencyBands,
    IntentClassification, IntentType, APIResponse
)
from app.core.signal_processing import SignalProcessor
from app.core.ai_firewall import intent_classifier
from app.core.privacy_engine import PrivacyEngine
from app.utils.eeg_generator import SyntheticEEGGenerator
from app.config import settings

router = APIRouter()

# Initialize components
signal_processor = SignalProcessor(settings.SAMPLING_RATE)
privacy_engine = PrivacyEngine(settings.DEFAULT_EPSILON, settings.DEFAULT_DELTA)
eeg_generator = SyntheticEEGGenerator(settings.SAMPLING_RATE, settings.NUM_CHANNELS)


@router.post("/process", response_model=SignalProcessingResult)
async def process_eeg_signal(signal_input: EEGSignalInput):
    """
    Process raw EEG signal through the complete neural firewall pipeline.
    
    Pipeline:
    1. Clean signal (noise removal)
    2. Extract frequency bands
    3. Classify intent (intentional vs subconscious)
    4. Apply differential privacy
    5. Detect threats
    
    Returns processed, privacy-protected neural data.
    """
    try:
        # Step 1: Process signal and extract features
        features, cleaned_channels = signal_processor.process_pipeline(
            signal_input.channels,
            clean=True
        )
        
        # Step 2: Classify intent
        intent_type, confidence, explanation = intent_classifier.classify(features)
        
        # Step 3: Extract frequency bands
        bands = {
            'delta': features['delta'],
            'theta': features['theta'],
            'alpha': features['alpha'],
            'beta': features['beta'],
            'gamma': features['gamma']
        }
        
        # Step 4: Apply differential privacy
        privacy_level = settings.DEFAULT_PRIVACY_LEVEL
        protected_bands = privacy_engine.privatize_frequency_bands(
            bands,
            privacy_level=privacy_level
        )
        
        # Step 5: Create response
        result = SignalProcessingResult(
            original_channels=len(signal_input.channels),
            sampling_rate=signal_input.sampling_rate,
            frequency_bands=FrequencyBands(**protected_bands),
            intent_classification=IntentClassification(
                intent_type=IntentType(intent_type),
                confidence=confidence,
                explanation=explanation
            ),
            privacy_applied=True,
            threats_detected=[],  # Will be populated by threat detector
            timestamp=datetime.now()
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signal processing failed: {str(e)}")


@router.post("/synthetic", response_model=APIResponse)
async def generate_synthetic_eeg(request: SyntheticEEGRequest):
    """
    Generate synthetic EEG data for testing.
    
    Useful for frontend integration and demos without real BCI hardware.
    """
    try:
        # Generate synthetic EEG
        synthetic_data = eeg_generator.generate(
            duration=request.duration,
            brain_state=request.brain_state
        )
        
        return APIResponse(
            success=True,
            message=f"Generated {request.duration}s of synthetic EEG ({request.brain_state} state)",
            data={
                "channels": synthetic_data,
                "sampling_rate": request.sampling_rate,
                "num_channels": request.num_channels,
                "brain_state": request.brain_state,
                "duration": request.duration
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EEG generation failed: {str(e)}")


@router.get("/bands/{channel_count}")
async def get_frequency_bands_info(channel_count: int):
    """
    Get information about EEG frequency bands.
    Educational endpoint for understanding the data.
    """
    return APIResponse(
        success=True,
        message="EEG frequency band information",
        data={
            "bands": {
                "delta": {
                    "range": "0.5-4 Hz",
                    "description": "Deep sleep, unconscious processes"
                },
                "theta": {
                    "range": "4-8 Hz",
                    "description": "Drowsiness, meditation, memory, emotion"
                },
                "alpha": {
                    "range": "8-13 Hz",
                    "description": "Relaxation, calm, closed eyes"
                },
                "beta": {
                    "range": "13-30 Hz",
                    "description": "Active thinking, focus, motor planning"
                },
                "gamma": {
                    "range": "30-100 Hz",
                    "description": "High-level cognition, perception, consciousness"
                }
            },
            "recommended_channels": max(8, min(channel_count, 32)),
            "sampling_rate": settings.SAMPLING_RATE
        }
    )
