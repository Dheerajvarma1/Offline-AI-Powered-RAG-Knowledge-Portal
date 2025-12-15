"""Generate embeddings using lightweight sentence transformers."""
import torch
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer

from utils.config_loader import ConfigLoader
from utils.memory_monitor import MemoryMonitor


class EmbeddingGenerator:
    """Generate embeddings using sentence transformers (optimized for 8GB RAM)."""
    
    def __init__(self, config: ConfigLoader):
        self.config = config
        self.memory_monitor = MemoryMonitor(
            max_memory_mb=config.get('memory.max_memory_usage_mb', 6000)
        )
        
        model_name = config.get('embedding.model_name', 'sentence-transformers/all-MiniLM-L6-v2')
        device = config.get('embedding.device', 'cpu')
        batch_size = config.get('embedding.batch_size', 32)
        
        # Load model (will download on first run if not cached)
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        self.batch_size = batch_size
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        print(f"Embedding model loaded. Dimension: {self.dimension}")
    
    def generate_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text(s)."""
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return np.array([])
        
        # Process in batches to manage memory
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            # Check memory before processing batch
            if not self.memory_monitor.check_memory_available():
                self.memory_monitor.force_gc()
            
            # Generate embeddings
            embeddings = self.model.encode(
                batch,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True  # Normalize for better similarity search
            )
            
            all_embeddings.append(embeddings)
        
        # Concatenate all batches
        result = np.vstack(all_embeddings) if len(all_embeddings) > 1 else all_embeddings[0]
        
        return result
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.dimension



