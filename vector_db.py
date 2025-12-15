"""Vector database management using FAISS for efficient similarity search."""
import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from utils.config_loader import ConfigLoader
from utils.memory_monitor import MemoryMonitor


class VectorDatabase:
    """Manage vector embeddings and similarity search using FAISS."""
    
    def __init__(self, config: ConfigLoader):
        self.config = config
        self.memory_monitor = MemoryMonitor(
            max_memory_mb=config.get('memory.max_memory_usage_mb', 6000)
        )
        
        self.dimension = config.get('vector_db.dimension', 384)
        self.index_path = Path(config.get('vector_db.save_path', './data/vector_index'))
        self.metadata_path = self.index_path / 'metadata.pkl'
        
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict] = []
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create a new one."""
        index_file = self.index_path / 'index.faiss'
        
        if index_file.exists() and self.metadata_path.exists():
            try:
                self.index = faiss.read_index(str(index_file))
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                # Check for compatibility (must support add_with_ids)
                # IndexIDMap supports add_with_ids, IndexFlatL2 doesn't
                try:
                    # Test if index supports ID mapping
                    if not isinstance(self.index, faiss.IndexIDMap):
                         print("Detected legacy index format. Upgrading to IndexIDMap...")
                         # We cannot easily migrate vectors, so we rebuild
                         self._create_new_index()
                    else:
                        print(f"Loaded existing index with {self.index.ntotal} vectors")
                except Exception:
                     self._create_new_index()

            except Exception as e:
                print(f"Error loading index: {e}. Creating new index.")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index with ID mapping."""
        # Use IndexIDMap to support deletion/ID mapping
        base_index = faiss.IndexFlatL2(self.dimension)
        self.index = faiss.IndexIDMap(base_index)
        self.metadata = []
        print("Created new FAISS index with IDMap")

    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict]):
        """Add vectors and their metadata to the index."""
        if len(vectors) == 0:
            return
        
        # Ensure vectors are float32 and correct shape
        vectors = np.array(vectors, dtype=np.float32)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        
        # Check dimension
        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Vector dimension mismatch: expected {self.dimension}, "
                f"got {vectors.shape[1]}"
            )
        
        # Generate IDs
        start_id = 0
        if self.metadata:
            # excessive safety: find max ID used so far
            start_id = max(m.get('vector_id', 0) for m in self.metadata) + 1
            
        ids = np.arange(start_id, start_id + len(vectors))
        
        # Add to index with IDs
        self.index.add_with_ids(vectors, ids)
        
        # Add metadata
        for i, meta in enumerate(metadata):
            meta['vector_id'] = int(ids[i])
            self.metadata.append(meta)
        
        # Memory check
        if not self.memory_monitor.check_memory_available():
            self.memory_monitor.force_gc()
            
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict]:
        """Search for similar vectors."""
        print(f"DEBUG: VDB Search - Index Total: {self.index.ntotal}, Metadata Len: {len(self.metadata)}")
        if self.index.ntotal == 0:
            return []
        
        # Ensure query vector is correct format
        query_vector = np.array(query_vector, dtype=np.float32)
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # Perform search
        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
        print(f"DEBUG: VDB Search - Indices: {indices}, Distances: {distances}")
        
        # Retrieve results with metadata using vector_id map
        id_to_meta = {m['vector_id']: m for m in self.metadata}
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1 and idx in id_to_meta:
                result = id_to_meta[idx].copy()
                result['distance'] = float(distance)
                result['score'] = 1 / (1 + distance)  # Convert distance to similarity score
                results.append(result)
        
        return results

    def save(self):
        """Save index and metadata to disk."""
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        index_file = self.index_path / 'index.faiss'
        faiss.write_index(self.index, str(index_file))
        
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        print(f"Saved index with {self.index.ntotal} vectors")

    def get_stats(self) -> Dict:
        """Get statistics about the vector database."""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.dimension,
            'index_type': type(self.index).__name__,
            'metadata_count': len(self.metadata)
        }

    def delete_by_file_hash(self, file_hash: str) -> int:
        """Delete vectors associated with a file hash."""
        ids_to_remove = [
            m['vector_id'] for m in self.metadata
            if m.get('file_hash') == file_hash
        ]
        
        if not ids_to_remove:
            return 0
            
        # Remove from FAISS index
        ids_array = np.array(ids_to_remove, dtype=np.int64)
        self.index.remove_ids(ids_array)
        
        # Remove from metadata
        self.metadata = [m for m in self.metadata if m.get('file_hash') != file_hash]
        
        return len(ids_to_remove)



