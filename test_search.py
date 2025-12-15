from utils.config_loader import ConfigLoader
from vector_db import VectorDatabase
from embedding_generator import EmbeddingGenerator
import os

print("Initializing components...")
config = ConfigLoader()
vdb = VectorDatabase(config)
emb = EmbeddingGenerator(config)

print(f"\nDB contains {vdb.index.ntotal} vectors")

query = "Dheeraj"
print(f"\nGenerating embedding for query: '{query}'")
query_vec = emb.generate_embeddings(query)

print("Searching...")
results = vdb.search(query_vec, k=5)

print(f"\nFound {len(results)} results:")
for r in results:
    print(f" - {r.get('file_name')} (Score: {r.get('score'):.4f})")
    print(f"   Text: {r.get('text')[:50]}...")

if len(results) == 0:
    print("\nNO RESULTS FOUND.")
    print("This suggests the index might be empty or valid vectors are not being returned.")
    print("Metadata check:")
    print(f"Metadata count: {len(vdb.metadata)}")
    if len(vdb.metadata) > 0:
        print(f"First metadata item: {vdb.metadata[0]}")
