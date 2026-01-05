"""
AI Firewall - Intent Classification and Permission Gating.
The core neural security layer that distinguishes intentional from subconscious data.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime
import uuid


class IntentClassifier:
    """
    Classify neural signals as intentional commands vs subconscious leakage.
    
    Uses machine learning trained on EEG feature patterns.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize intent classifier.
        
        Args:
            model_path: Path to pre-trained model (None = use rule-based)
        """
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path
        
        # Try to load pre-trained model
        if model_path and os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                print(f"Loaded intent classifier from {model_path}")
            except Exception as e:
                print(f"Could not load model: {e}, using rule-based classification")
    
    def classify(self, features: Dict[str, float]) -> Tuple[str, float, str]:
        """
        Classify neural intent from EEG features.
        
        Args:
            features: EEG features (band powers, ratios, etc.)
            
        Returns:
            Tuple of (intent_type, confidence, explanation)
            - intent_type: 'intentional', 'subconscious', or 'neutral'
            - confidence: 0.0 to 1.0
            - explanation: Human-readable reasoning
        """
        if self.model is not None:
            return self._ml_classify(features)
        else:
            return self._rule_based_classify(features)
    
    def _rule_based_classify(self, features: Dict[str, float]) -> Tuple[str, float, str]:
        """
        Rule-based classification using neuroscience principles.
        
        Intentional Commands:
        - High Beta (focus, motor planning)
        - Moderate Gamma (active processing)
        - Lower Theta/Alpha ratio
        
        Subconscious Activity:
        - High Theta (emotion, memory)
        - High Gamma (anxiety, stress)
        - Low Beta (lack of focus)
        """
        beta = features.get('beta', 0)
        alpha = features.get('alpha', 0)
        theta = features.get('theta', 0)
        gamma = features.get('gamma', 0)
        delta = features.get('delta', 0)
        
        # Calculate ratios
        beta_alpha_ratio = beta / (alpha + 1e-10)
        theta_alpha_ratio = theta / (alpha + 1e-10)
        
        # Decision logic
        score = 0
        reasons = []
        
        # Intentional markers (positive score)
        if beta > 15:  # Strong beta indicates focus
            score += 2
            reasons.append("strong beta (focus)")
        
        if beta_alpha_ratio > 1.5:  # High beta/alpha suggests engagement
            score += 1
            reasons.append("high beta/alpha ratio")
        
        if gamma > 10 and gamma < 30:  # Moderate gamma is good
            score += 1
            reasons.append("controlled gamma")
        
        # Subconscious markers (negative score)
        if theta > 20:  # High theta suggests emotion/memory
            score -= 2
            reasons.append("elevated theta (emotional)")
        
        if gamma > 40:  # Very high gamma indicates stress
            score -= 2
            reasons.append("high gamma (stress)")
        
        if theta_alpha_ratio > 1.0:  # Drowsiness or emotional state
            score -= 1
            reasons.append("high theta/alpha")
        
        if beta < 10:  # Low beta = lack of intentional focus
            score -= 1
            reasons.append("low beta")
        
        # Classification
        if score >= 2:
            intent = "intentional"
            confidence = min(0.9, 0.5 + score * 0.1)
            explanation = f"Intentional command detected: {', '.join(reasons[:2])}"
        elif score <= -2:
            intent = "subconscious"
            confidence = min(0.9, 0.5 + abs(score) * 0.1)
            explanation = f"Subconscious activity detected: {', '.join(reasons[:2])}"
        else:
            intent = "neutral"
            confidence = 0.6
            explanation = "Neutral brain state, no clear intent"
        
        return intent, confidence, explanation
    
    def _ml_classify(self, features: Dict[str, float]) -> Tuple[str, float, str]:
        """ML-based classification using trained model."""
        # Extract feature vector
        feature_vector = self._extract_feature_vector(features)
        
        # Predict
        prediction = self.model.predict([feature_vector])[0]
        probabilities = self.model.predict_proba([feature_vector])[0]
        
        intent_map = {0: 'intentional', 1: 'subconscious', 2: 'neutral'}
        intent = intent_map.get(prediction, 'neutral')
        confidence = float(max(probabilities))
        
        explanation = f"ML model classified as {intent} with {confidence:.2%} confidence"
        
        return intent, confidence, explanation
    
    def _extract_feature_vector(self, features: Dict[str, float]) -> np.ndarray:
        """Convert feature dict to numpy array for ML model."""
        # Standard feature order
        feature_names = ['delta', 'theta', 'alpha', 'beta', 'gamma', 
                        'beta_alpha_ratio', 'gamma_beta_ratio']
        
        vector = [features.get(name, 0.0) for name in feature_names]
        return np.array(vector)


class PermissionGate:
    """
    Permission-based firewall for neural data.
    Controls what data apps can access based on user permissions.
    """
    
    def __init__(self):
        """Initialize permission gate."""
        self.permissions = {}  # app_id -> list of granted permissions
        self.audit_log = []
    
    def grant_permission(self, app_id: str, app_name: str, permission_type: str):
        """Grant a permission to an app."""
        if app_id not in self.permissions:
            self.permissions[app_id] = {
                'app_name': app_name,
                'granted': []
            }
        
        if permission_type not in self.permissions[app_id]['granted']:
            self.permissions[app_id]['granted'].append(permission_type)
            
            # Log the grant
            self.audit_log.append({
                'app_id': app_id,
                'app_name': app_name,
                'action': 'grant',
                'permission': permission_type,
                'timestamp': datetime.now().isoformat()
            })
    
    def revoke_permission(self, app_id: str, permission_type: str):
        """Revoke a permission from an app."""
        if app_id in self.permissions:
            if permission_type in self.permissions[app_id]['granted']:
                self.permissions[app_id]['granted'].remove(permission_type)
                
                # Log the revocation
                self.audit_log.append({
                    'app_id': app_id,
                    'app_name': self.permissions[app_id]['app_name'],
                    'action': 'revoke',
                    'permission': permission_type,
                    'timestamp': datetime.now().isoformat()
                })
    
    def check_permission(self, app_id: str, permission_type: str) -> bool:
        """Check if app has a specific permission."""
        if app_id not in self.permissions:
            return False
        return permission_type in self.permissions[app_id]['granted']
    
    def filter_data(self, 
                   app_id: str, 
                   data: Dict[str, float],
                   intent: str) -> Dict[str, float]:
        """
        Filter neural data based on app permissions.
        
        Args:
            app_id: Application requesting data
            data: Full neural data (frequency bands, features)
            intent: Classified intent type
            
        Returns:
            Filtered data containing only permitted fields
        """
        if app_id not in self.permissions:
            # No permissions = only basic motor intent
            return {'motor_intent': 1.0 if intent == 'intentional' else 0.0}
        
        granted = self.permissions[app_id]['granted']
        filtered = {}
        
        # Permission-based filtering
        if 'motor_intent' in granted:
            filtered['motor_intent'] = 1.0 if intent == 'intentional' else 0.0
            filtered['beta'] = data.get('beta', 0)
        
        if 'focus_level' in granted:
            filtered['beta_alpha_ratio'] = data.get('beta_alpha_ratio', 0)
        
        if 'emotional_state' in granted:
            filtered['theta'] = data.get('theta', 0)
            filtered['alpha'] = data.get('alpha', 0)
        
        if 'full_spectrum' in granted:
            # Grant all data (dangerous!)
            filtered = data.copy()
        
        return filtered


class ThreatDetector:
    """Detect malicious patterns in neural data requests."""
    
    def __init__(self):
        """Initialize threat detector."""
        self.threat_log = []
    
    def detect_threats(self,
                      app_id: str,
                      requested_permissions: List[str],
                      request_frequency: int = 1) -> List[Dict]:
        """
        Detect potential threats in app behavior.
        
        Args:
            app_id: Application ID
            requested_permissions: List of requested permissions
            request_frequency: Requests per second
            
        Returns:
            List of threat alerts
        """
        threats = []
        
        # Threat 1: Requesting full spectrum without justification
        if 'full_spectrum' in requested_permissions:
            threats.append({
                'threat_id': str(uuid.uuid4()),
                'threat_type': 'excessive_permissions',
                'level': 'high',
                'description': f'App {app_id} requesting full neural spectrum access',
                'app_id': app_id,
                'mitigated': False
            })
        
        # Threat 2: High request frequency (data harvesting)
        if request_frequency > 10:
            threats.append({
                'threat_id': str(uuid.uuid4()),
                'threat_type': 'data_harvesting',
                'level': 'medium',
                'description': f'Unusual request frequency: {request_frequency}/sec',
                'app_id': app_id,
                'mitigated': False
            })
        
        # Threat 3: Emotional data without motor intent permission
        if 'emotional_state' in requested_permissions and 'motor_intent' not in requested_permissions:
            threats.append({
                'threat_id': str(uuid.uuid4()),
                'threat_type': 'emotional_surveillance',
                'level': 'critical',
                'description': 'App requesting emotional data without primary functionality need',
                'app_id': app_id,
                'mitigated': False
            })
        
        # Log all threats
        for threat in threats:
            threat['timestamp'] = datetime.now().isoformat()
            self.threat_log.append(threat)
        
        return threats


# Global instances (in real app, use dependency injection)
intent_classifier = IntentClassifier()
permission_gate = PermissionGate()
threat_detector = ThreatDetector()
