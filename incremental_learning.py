"""Incremental learning system for continuous knowledge base updates."""
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from knowledge_manager import KnowledgeManager
from utils.config_loader import ConfigLoader


class IncrementalLearning:
    """Manage incremental updates to the knowledge base."""
    
    def __init__(self, config: ConfigLoader, knowledge_manager: KnowledgeManager):
        self.config = config
        self.knowledge_manager = knowledge_manager
        self.enabled = config.get('incremental.enabled', True)
        self.update_frequency = config.get('incremental.update_frequency', 'immediate')
    
    def process_new_documents(self, file_paths: List[str], uploaded_by: str) -> Dict:
        """Process new documents with incremental learning."""
        if not self.enabled:
            return self.knowledge_manager.add_documents_batch(file_paths, uploaded_by)
        
        results = []
        for file_path in file_paths:
            # Check if document exists (by content hash)
            result = self.knowledge_manager.add_document(file_path, uploaded_by)
            
            # If document exists, update it
            if result['status'] == 'exists':
                file_path_obj = Path(file_path)
                with open(file_path_obj, 'rb') as f:
                    import hashlib
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                # Update existing document
                update_result = self.knowledge_manager.update_document(file_hash, uploaded_by)
                result = update_result
            
            results.append(result)
        
        return results
    
    def detect_changes(self, directory: str) -> List[Dict]:
        """Detect changed files in a directory (for scheduled updates)."""
        # This would scan a directory and detect new/modified files
        # For now, returns empty list - can be extended
        return []
    
    def rebuild_index_if_needed(self, threshold: int = 1000) -> bool:
        """Rebuild index if it becomes too fragmented."""
        stats = self.knowledge_manager.get_statistics()
        total_vectors = stats.get('total_vectors', 0)
        
        # Simple heuristic: rebuild if we've deleted many documents
        # In production, track deletions and rebuild when threshold reached
        return False  # Placeholder



