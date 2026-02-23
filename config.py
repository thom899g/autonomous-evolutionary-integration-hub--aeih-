"""
AEIH Configuration - Central configuration management for the Autonomous Evolutionary Integration Hub.
Handles environment variables, default settings, and validation.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

@dataclass
class FirebaseConfig:
    """Firebase configuration for state management and real-time updates"""
    project_id: str = os.getenv("FIREBASE_PROJECT_ID", "evolution-ecosystem")
    credentials_path: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")
    firestore_collection: str = os.getenv("FIRESTORE_COLLECTION", "aeih_modules")
    performance_collection: str = os.getenv("PERFORMANCE_COLLECTION", "aeih_performance")
    
@dataclass
class MonitoringConfig:
    """Performance monitoring configuration"""
    sampling_interval: int = int(os.getenv("SAMPLING_INTERVAL", "60"))  # seconds
    retention_days: int = int(os.getenv("RETENTION_DAYS", "30"))
    anomaly_threshold: float = float(os.getenv("ANOMALY_THRESHOLD", "2.0"))
    
@dataclass
class OptimizationConfig:
    """Optimization engine configuration"""
    retrain_interval: int = int(os.getenv("RETRAIN_INTERVAL", "3600"))  # seconds
    min_samples_for_training: int = int(os.getenv("MIN_SAMPLES_TRAINING", "100"))
    optimization_window: int = int(os.getenv("OPTIMIZATION_WINDOW", "24"))  # hours
    
class AEIHConfig:
    """Main configuration class with validation"""
    
    def __init__(self):
        self.firebase = FirebaseConfig()
        self.monitoring = MonitoringConfig()
        self.optimization = OptimizationConfig()
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Validate configurations
        self._validate()
    
    def _validate(self):
        """Validate all configurations"""
        if not os.path.exists(self.firebase.credentials_path):
            logging.warning(f"Firebase credentials not found at {self.firebase.credentials_path}")
            
        if self.monitoring.sampling_interval < 5:
            raise ValueError("Sampling interval must be at least 5 seconds")
            
        if self.optimization.min_samples_for_training < 10:
            raise ValueError("Minimum samples for training must be at least 10")
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary for logging"""
        return {
            "firebase": self.firebase.__dict__,
            "monitoring": self.monitoring.__dict__,
            "optimization": self.optimization.__dict__,
            "log_level": self.log_level
        }

# Global configuration instance
config = AEIHConfig()