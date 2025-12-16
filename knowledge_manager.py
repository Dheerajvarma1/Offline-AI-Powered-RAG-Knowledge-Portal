"""Main knowledge manager that orchestrates document processing and indexing."""
import os
from pathlib import Path
from typing import List, Dict, Optional

from document_processor import DocumentProcessor
from embedding_generator import EmbeddingGenerator
from vector_db import VectorDatabase
from database import Database
from utils.config_loader import ConfigLoader
from utils.memory_monitor import MemoryMonitor


class KnowledgeManager:
    """Orchestrates the entire knowledge management pipeline."""
    
    def __init__(self, config: ConfigLoader, vector_db: VectorDatabase = None):
        self.config = config
        self.memory_monitor = MemoryMonitor(
            max_memory_mb=config.get('memory.max_memory_usage_mb', 6000)
        )
        
        # Initialize components
        self.doc_processor = DocumentProcessor(config)
        self.embedding_gen = EmbeddingGenerator(config)
        self.vector_db = vector_db if vector_db else VectorDatabase(config)
        self.database = Database(config)
        
        # Ensure documents directory exists
        self.documents_dir = Path(config.get('app.documents_dir', './data/documents'))
        self.documents_dir.mkdir(parents=True, exist_ok=True)
    
    def add_document(self, file_path: str, uploaded_by: str, 
                    permissions: Dict = None, department: str = None) -> Dict:
        """Add a document to the knowledge base."""
        file_path = Path(file_path)
        
        # Check if document already exists
        with open(file_path, 'rb') as f:
            import hashlib
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        existing_doc = self.database.get_document_by_hash(file_hash)
        if existing_doc:
            return {
                'status': 'exists',
                'message': f'Document {file_path.name} already exists in the knowledge base.',
                'document_id': existing_doc['id']
            }
        
        # Copy file to documents directory
        dest_path = self.documents_dir / file_path.name
        import shutil
        shutil.copy2(file_path, dest_path)
        
        try:
            # Process document
            processed = self.doc_processor.process_document(str(dest_path))
            
            # Generate embeddings for chunks
            chunk_texts = [chunk['text'] for chunk in processed['chunks']]
            embeddings = self.embedding_gen.generate_embeddings(chunk_texts)
            
            # Prepare metadata for vector DB
            vector_metadata = []
            for i, chunk in enumerate(processed['chunks']):
                vector_metadata.append({
                    'file_name': processed['file_name'],
                    'file_path': str(dest_path),
                    'file_hash': processed['file_hash'],
                    'chunk_id': chunk['chunk_id'],
                    'text': chunk['text'],
                    'start_pos': chunk['start_pos'],
                    'end_pos': chunk['end_pos'],
                    'department': department # Add department to vector metadata
                })
            
            # Add to vector database
            self.vector_db.add_vectors(embeddings, vector_metadata)
            
            # Save vector database
            self.vector_db.save()
            
            # Add to SQLite database
            doc_id = self.database.add_document(
                file_name=processed['file_name'],
                file_path=str(dest_path),
                file_hash=processed['file_hash'],
                file_size=processed['file_size'],
                file_type=dest_path.suffix,
                chunk_count=processed['chunk_count'],
                uploaded_by=uploaded_by,
                permissions=permissions,
                department=department
            )
            
            return {
                'status': 'success',
                'message': f'Document {file_path.name} added successfully.',
                'document_id': doc_id,
                'chunks': processed['chunk_count']
            }
        
        except Exception as e:
            # Clean up on error
            if dest_path.exists():
                dest_path.unlink()
            return {
                'status': 'error',
                'message': f'Error processing document: {str(e)}'
            }
    
    def add_documents_batch(self, file_paths: List[str], uploaded_by: str) -> List[Dict]:
        """Add multiple documents in batch (with memory management)."""
        results = []
        batch_size = self.config.get('incremental.batch_size', 10)
        
        for i, file_path in enumerate(file_paths):
            # Check memory before processing
            if not self.memory_monitor.check_memory_available():
                self.memory_monitor.force_gc()
            
            result = self.add_document(file_path, uploaded_by)
            results.append(result)
            
            # Save periodically
            if (i + 1) % batch_size == 0:
                self.vector_db.save()
                self.memory_monitor.force_gc()
        
        # Final save
        self.vector_db.save()
        return results
    
    def update_document(self, file_hash: str, uploaded_by: str) -> Dict:
        """Update an existing document (incremental learning)."""
        # Delete old version
        self.delete_document(file_hash)
        
        # Get file path
        doc = self.database.get_document_by_hash(file_hash)
        if not doc:
            return {'status': 'error', 'message': 'Document not found'}
        
        file_path = Path(doc['file_path'])
        if not file_path.exists():
            return {'status': 'error', 'message': 'File not found on disk'}
        
        # Re-add document
        return self.add_document(str(file_path), uploaded_by, doc.get('permissions'))
    
    def delete_document(self, file_hash: str) -> bool:
        """Delete a document from the knowledge base."""
        # Delete from vector DB
        deleted_count = self.vector_db.delete_by_file_hash(file_hash)
        
        # Delete from SQLite
        self.database.delete_document(file_hash)
        
        # Delete file
        doc = self.database.get_document_by_hash(file_hash)
        if doc:
            file_path = Path(doc['file_path'])
            if file_path.exists():
                file_path.unlink()
        
        # Save vector DB
        self.vector_db.save()
        
        return deleted_count > 0
    
    def get_statistics(self) -> Dict:
        """Get knowledge base statistics."""
        vector_stats = self.vector_db.get_stats()
        documents = self.database.get_all_documents()
        memory_status = self.memory_monitor.get_memory_usage()
        
        return {
            'total_documents': len(documents),
            'total_vectors': vector_stats['total_vectors'],
            'total_chunks': sum(doc.get('chunk_count', 0) for doc in documents),
            'memory_usage': memory_status,
            'vector_db_dimension': vector_stats['dimension']
        }



