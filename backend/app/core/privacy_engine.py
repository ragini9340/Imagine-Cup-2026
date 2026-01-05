"""
Differential Privacy Engine for Neural Data Protection.
Implements Laplacian noise mechanism for privacy preservation.
"""

import numpy as np
from typing import Dict, Any
import copy


class PrivacyEngine:
    """
    Add differential privacy to neural data.
    Prevents brain fingerprinting while maintaining utility.
    """
    
    def __init__(self, 
                 epsilon: float = 1.0,
                 delta: float = 1e-5):
        """
        Initialize privacy engine.
        
        Args:
            epsilon: Privacy budget (lower = more privacy, less utility)
            delta: Probability of privacy breach (typically ~1e-5)
        """
        self.epsilon = epsilon
        self.delta = delta
    
    def add_laplacian_noise(self, 
                           value: float,
                           sensitivity: float = 1.0) -> float:
        """
        Add Laplacian noise to a single value.
        
        Args:
            value: Original value
            sensitivity: Sensitivity of the query (max change from one record)
            
        Returns:
            Noisy value
        """
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return value + noise
    
    def privatize_frequency_bands(self,
                                  bands: Dict[str, float],
                                  privacy_level: float = 0.5) -> Dict[str, float]:
        """
        Apply differential privacy to frequency band data.
        
        Args:
            bands: Frequency band powers (delta, theta, alpha, beta, gamma)
            privacy_level: 0.0 = max privacy, 1.0 = max utility
            
        Returns:
            Privacy-protected frequency bands
        """
        # Adjust noise based on privacy level
        # Lower privacy_level = more noise
        effective_epsilon = self.epsilon * (privacy_level + 0.1)
        
        privatized = {}
        for band_name, power in bands.items():
            # Add noise scaled by current epsilon
            scale = 1.0 / effective_epsilon
            noise = np.random.laplace(0, scale)
            
            # Ensure non-negative power values
            privatized[band_name] = max(0.0, power + noise)
        
        return privatized
    
    def apply_privacy(self,
                     data: Dict[str, Any],
                     privacy_level: float = 0.5,
                     protect_fields: list = None) -> Dict[str, Any]:
        """
        Apply differential privacy to specified fields in data.
        
        Args:
            data: Data dictionary to protect
            privacy_level: Privacy vs utility tradeoff (0.0 - 1.0)
            protect_fields: List of field names to protect (None = all numeric)
            
        Returns:
            Privacy-protected data
        """
        protected_data = copy.deepcopy(data)
        
        # If no fields specified, protect all numeric fields
        if protect_fields is None:
            protect_fields = [k for k, v in data.items() if isinstance(v, (int, float))]
        
        # Adjust epsilon based on privacy level
        effective_epsilon = self.epsilon * (privacy_level + 0.1)
        
        for field in protect_fields:
            if field in protected_data and isinstance(protected_data[field], (int, float)):
                scale = 1.0 / effective_epsilon
                noise = np.random.laplace(0, scale)
                protected_data[field] = protected_data[field] + noise
        
        return protected_data
    
    def mask_sensitive_data(self,
                           data: Dict[str, Any],
                           sensitivity_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Completely mask highly sensitive data fields.
        
        Args:
            data: Data dictionary
            sensitivity_threshold: Threshold for masking (0.0 - 1.0)
            
        Returns:
            Masked data
        """
        masked_data = copy.deepcopy(data)
        
        # Define sensitive fields (those revealing subconscious state)
        # These are typically emotional/memory indicators
        sensitive_fields = [
            'theta',  # Associated with memory, emotion
            'gamma',  # High-level cognition, can reveal stress
        ]
        
        # If privacy is very high (low threshold), mask sensitive fields
        if sensitivity_threshold < 0.3:
            for field in sensitive_fields:
                if field in masked_data:
                    masked_data[field] = 0.0  # Completely mask
        
        return masked_data
    
    def calculate_privacy_loss(self, 
                              queries_made: int) -> float:
        """
        Calculate cumulative privacy loss after multiple queries.
        
        Args:
            queries_made: Number of queries processed
            
        Returns:
            Total privacy loss (epsilon)
        """
        # Privacy loss accumulates linearly for basic composition
        total_epsilon = self.epsilon * queries_made
        return total_epsilon


# Convenience function
def apply_differential_privacy(
    frequency_bands: Dict[str, float],
    privacy_level: float = 0.5,
    epsilon: float = 1.0
) -> Dict[str, float]:
    """
    Quick function to add differential privacy to frequency bands.
    
    Args:
        frequency_bands: EEG frequency band powers
        privacy_level: Privacy setting (0.0 = max privacy, 1.0 = max utility)
        epsilon: Privacy budget
        
    Returns:
        Privacy-protected frequency bands
    """
    engine = PrivacyEngine(epsilon=epsilon)
    return engine.privatize_frequency_bands(frequency_bands, privacy_level)
