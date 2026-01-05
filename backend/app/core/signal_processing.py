"""
Signal Processing Pipeline for EEG Data.
Handles noise removal, artifact filtering, and frequency decomposition.
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import Dict, List, Tuple
import mne
from mne import create_info
from mne.io import RawArray


class SignalProcessor:
    """Process raw EEG signals for neural firewall analysis."""
    
    def __init__(self, sampling_rate: int = 256):
        """
        Initialize signal processor.
        
        Args:
            sampling_rate: Sampling frequency in Hz
        """
        self.sampling_rate = sampling_rate
        
        # Define frequency bands (Hz)
        self.bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 100)
        }
    
    def clean_signal(self, 
                     channels: Dict[str, List[float]],
                     apply_notch: bool = True,
                     apply_bandpass: bool = True) -> Dict[str, List[float]]:
        """
        Remove noise and artifacts from raw EEG signal.
        
        Args:
            channels: Multi-channel EEG data
            apply_notch: Remove 50/60Hz power line noise
            apply_bandpass: Apply bandpass filter (0.5-100Hz)
            
        Returns:
            Cleaned EEG signal
        """
        # Convert to numpy arrays
        channel_names = list(channels.keys())
        data = np.array([channels[ch] for ch in channel_names])
        
        # Create MNE RawArray for advanced filtering
        info = create_info(
            ch_names=channel_names,
            sfreq=self.sampling_rate,
            ch_types='eeg'
        )
        raw = RawArray(data, info, verbose=False)
        
        # Apply notch filter (remove power line noise at 50Hz/60Hz)
        if apply_notch:
            raw.notch_filter(
                freqs=[50, 60],
                verbose=False
            )
        
        # Apply bandpass filter (0.5-100 Hz keeps relevant EEG)
        if apply_bandpass:
            raw.filter(
                l_freq=0.5,
                h_freq=100,
                verbose=False
            )
        
        # Convert back to dictionary format
        cleaned_data = raw.get_data()
        cleaned_channels = {
            ch: cleaned_data[i].tolist()
            for i, ch in enumerate(channel_names)
        }
        
        return cleaned_channels
    
    def extract_frequency_bands(self, 
                                channels: Dict[str, List[float]]) -> Dict[str, float]:
        """
        Extract power in each frequency band using FFT.
        
        Args:
            channels: Multi-channel EEG data
            
        Returns:
            Dictionary of band powers (average across channels)
        """
        band_powers = {band: [] for band in self.bands.keys()}
        
        # Process each channel
        for channel_name, data in channels.items():
            data_array = np.array(data)
            
            # Compute FFT
            n = len(data_array)
            freqs = fftfreq(n, 1/self.sampling_rate)
            fft_vals = fft(data_array)
            power = np.abs(fft_vals) ** 2
            
            # Extract power for each band
            for band_name, (low, high) in self.bands.items():
                # Find frequencies in this band
                idx = np.where((freqs >= low) & (freqs <= high))
                
                # Calculate average power in band
                if len(idx[0]) > 0:
                    band_power = np.mean(power[idx])
                    band_powers[band_name].append(band_power)
        
        # Average across all channels
        avg_band_powers = {
            band: float(np.mean(powers)) if powers else 0.0
            for band, powers in band_powers.items()
        }
        
        return avg_band_powers
    
    def compute_features(self, 
                        channels: Dict[str, List[float]]) -> Dict[str, float]:
        """
        Compute comprehensive features for ML classification.
        
        Args:
            channels: Multi-channel EEG data
            
        Returns:
            Feature dictionary for AI firewall
        """
        # Get frequency band powers
        band_powers = self.extract_frequency_bands(channels)
        
        # Calculate additional features
        all_data = np.concatenate([np.array(data) for data in channels.values()])
        
        features = {
            **band_powers,  # Include all band powers
            'mean_amplitude': float(np.mean(np.abs(all_data))),
            'std_amplitude': float(np.std(all_data)),
            'beta_alpha_ratio': band_powers['beta'] / (band_powers['alpha'] + 1e-10),
            'gamma_beta_ratio': band_powers['gamma'] / (band_powers['beta'] + 1e-10),
            'num_channels': len(channels)
        }
        
        return features
    
    def process_pipeline(self, 
                        channels: Dict[str, List[float]],
                        clean: bool = True) -> Tuple[Dict[str, float], Dict[str, List[float]]]:
        """
        Complete signal processing pipeline.
        
        Args:
            channels: Raw multi-channel EEG data
            clean: Whether to apply noise removal
            
        Returns:
            Tuple of (features, cleaned_channels)
        """
        # Step 1: Clean signal
        if clean:
            cleaned = self.clean_signal(channels)
        else:
            cleaned = channels
        
        # Step 2: Extract features
        features = self.compute_features(cleaned)
        
        return features, cleaned


# Convenience function
def process_eeg_signal(channels: Dict[str, List[float]], 
                      sampling_rate: int = 256) -> Dict[str, float]:
    """
    Quick function to process EEG and extract frequency bands.
    
    Args:
        channels: Multi-channel EEG data
        sampling_rate: Sampling frequency
        
    Returns:
        Frequency band powers
    """
    processor = SignalProcessor(sampling_rate)
    features, _ = processor.process_pipeline(channels)
    return {
        'delta': features['delta'],
        'theta': features['theta'],
        'alpha': features['alpha'],
        'beta': features['beta'],
        'gamma': features['gamma']
    }
