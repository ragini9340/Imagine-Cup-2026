"""
Synthetic EEG Signal Generator for Neuro-Privacy Guard.
Creates realistic multi-channel EEG data for testing without hardware.
"""

import numpy as np
from typing import Dict, List, Literal
import mne


class SyntheticEEGGenerator:
    """Generate synthetic EEG signals mimicking real brain states."""
    
    def __init__(self, 
                 sampling_rate: int = 256,
                 num_channels: int = 8):
        """
        Initialize the EEG generator.
        
        Args:
            sampling_rate: Sampling frequency in Hz
            num_channels: Number of EEG channels
        """
        self.sampling_rate = sampling_rate
        self.num_channels = num_channels
        
        # Standard 10-20 EEG channel names
        self.channel_names = [
            'Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4',
            'O1', 'O2', 'F7', 'F8', 'T3', 'T4', 'T5', 'T6'
        ][:num_channels]
    
    def generate(self, 
                 duration: float = 2.0,
                 brain_state: Literal["focused", "relaxed", "stressed", "neutral"] = "neutral"
                ) -> Dict[str, List[float]]:
        """
        Generate synthetic EEG data.
        
        Args:
            duration: Signal duration in seconds
            brain_state: Target brain state to simulate
            
        Returns:
            Dictionary mapping channel names to signal arrays
        """
        n_samples = int(duration * self.sampling_rate)
        time = np.linspace(0, duration, n_samples)
        
        # Generate base signals for each channel
        signals = {}
        
        for channel in self.channel_names:
            # Create multi-frequency signal based on brain state
            signal = self._generate_channel_signal(time, brain_state)
            
            # Add realistic noise
            noise = np.random.normal(0, 0.1, n_samples)
            signal = signal + noise
            
            signals[channel] = signal.tolist()
        
        return signals
    
    def _generate_channel_signal(self, 
                                  time: np.ndarray, 
                                  brain_state: str) -> np.ndarray:
        """
        Generate signal for a single channel based on brain state.
        
        Brain states have characteristic frequency band profiles:
        - Focused: High beta (13-30Hz), moderate gamma
        - Relaxed: High alpha (8-13Hz), low beta
        - Stressed: High beta, high gamma, elevated theta
        - Neutral: Balanced across bands
        """
        signal = np.zeros_like(time)
        
        # Define frequency band characteristics for each state
        if brain_state == "focused":
            # High beta (focus, concentration)
            signal += 0.6 * np.sin(2 * np.pi * 20 * time)  # Beta
            signal += 0.3 * np.sin(2 * np.pi * 40 * time)  # Gamma
            signal += 0.2 * np.sin(2 * np.pi * 10 * time)  # Alpha
            
        elif brain_state == "relaxed":
            # High alpha (calm, relaxed)
            signal += 0.7 * np.sin(2 * np.pi * 10 * time)  # Alpha
            signal += 0.2 * np.sin(2 * np.pi * 6 * time)   # Theta
            signal += 0.1 * np.sin(2 * np.pi * 15 * time)  # Beta
            
        elif brain_state == "stressed":
            # High beta and gamma (anxiety, stress)
            signal += 0.7 * np.sin(2 * np.pi * 25 * time)  # High Beta
            signal += 0.5 * np.sin(2 * np.pi * 45 * time)  # Gamma
            signal += 0.4 * np.sin(2 * np.pi * 7 * time)   # Theta
            
        else:  # neutral
            # Balanced across bands
            signal += 0.3 * np.sin(2 * np.pi * 3 * time)   # Delta
            signal += 0.3 * np.sin(2 * np.pi * 6 * time)   # Theta
            signal += 0.4 * np.sin(2 * np.pi * 10 * time)  # Alpha
            signal += 0.3 * np.sin(2 * np.pi * 18 * time)  # Beta
            signal += 0.2 * np.sin(2 * np.pi * 35 * time)  # Gamma
        
        return signal
    
    def generate_with_intent(self, 
                            duration: float = 2.0,
                            intent: Literal["intentional", "subconscious"] = "intentional"
                           ) -> Dict[str, List[float]]:
        """
        Generate EEG data labeled by intent type.
        
        Args:
            duration: Signal duration in seconds
            intent: Type of neural activity
            
        Returns:
            Dictionary mapping channel names to signal arrays
        """
        if intent == "intentional":
            # Intentional commands = focused motor planning
            # Characterized by strong beta in motor cortex (C3, C4)
            return self.generate(duration, "focused")
        else:
            # Subconscious = emotional or memory-related
            # More theta/alpha, less organized beta
            return self.generate(duration, "stressed")


# Convenience function
def generate_synthetic_eeg(
    duration: float = 2.0,
    brain_state: str = "neutral",
    sampling_rate: int = 256,
    num_channels: int = 8
) -> Dict[str, List[float]]:
    """
    Quick function to generate synthetic EEG.
    
    Args:
        duration: Signal duration in seconds
        brain_state: Brain state to simulate
        sampling_rate: Sampling frequency in Hz
        num_channels: Number of channels
        
    Returns:
        Multi-channel EEG data
    """
    generator = SyntheticEEGGenerator(sampling_rate, num_channels)
    return generator.generate(duration, brain_state)
