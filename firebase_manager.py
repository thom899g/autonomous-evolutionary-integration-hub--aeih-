"""
Firebase Manager - Handles all Firebase interactions for the AEIH.
Provides robust state management, real-time updates, and error handling.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore, exceptions
from firebase_admin.firestore import SERVER_TIMESTAMP

from config import config

class FirebaseManager:
    """Manages Firebase connections and operations for AEIH"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_firebase()
        self.db = None
        self._listeners = {}
        
    def _initialize_firebase(self):
        """Initialize Firebase with error handling and fallbacks"""
        try:
            if not firebase_admin._apps:
                cred_path = config.firebase.credentials_path
                if cred_path:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {
                        'projectId': config.firebase.project_id
                    })
                else:
                    # Use default credentials (for GCP environments)
                    firebase_admin.initialize_app()
            
            self.db = firestore.client()
            self.logger.info("Firebase initialized successfully")
            
        except FileNotFoundError as e:
            self.logger.error(f"Firebase credentials not found: {e}")
            # Create a mock Firestore for development without Firebase
            self.db = MockFirestore()
        except exceptions.FirebaseError as e:
            self.logger.error(f"Firebase initialization failed: {e}")
            raise
    
    def register_module(self, module_id: str, module_data: Dict[str, Any]) -> bool:
        """
        Register a new module in Firestore with validation
        
        Args:
            module_id: Unique identifier for the module
            module_data: Module metadata including capabilities
            
        Returns:
            bool: Success status
        """
        try:
            if not module_id or not module_data:
                raise ValueError("Module ID and data are required")
            
            # Add metadata
            module_data.update({
                'registered_at': SERVER_TIMESTAMP,
                'last_seen': SERVER_TIMESTAMP,
                'status': 'active',
                'version': module_data.get('version', '1.0.0')
            })
            
            doc_ref = self.db.collection(config.firebase.firestore_collection).document(module_id)
            doc_ref.set(module_data, merge=True)
            
            self.logger.info(f"Module {module_id} registered successfully")
            return True
            
        except exceptions.FirebaseError as e:
            self.logger.error(f"Failed to register module {module_id}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error registering module: {e}")
            return False
    
    def update_module_status(self, module_id: str, status: str, metadata: Dict[str, Any] = None) -> bool:
        """Update module status and last seen timestamp"""
        try:
            update_data = {
                'status': status,
                'last_seen': SERVER_TIMESTAMP
            }
            
            if metadata:
                update_data.update(metadata)
            
            doc_ref = self.db.collection(config.firebase.firestore_collection).document(module_id)
            doc_ref.update(update_data)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to update module {module_id}: {e}")
            return False
    
    def log_performance(self, module_id: str, metrics: Dict[str, Any]) -> str:
        """
        Log performance