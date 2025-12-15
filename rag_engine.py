"""RAG (Retrieval-Augmented Generation) engine for query processing."""
import numpy as np
from typing import List, Dict, Optional
import requests
from llama_cpp import Llama

import google.generativeai as genai
from embedding_generator import EmbeddingGenerator
from vector_db import VectorDatabase
from utils.config_loader import ConfigLoader
from utils.memory_monitor import MemoryMonitor


class RAGEngine:
    """RAG engine that combines retrieval and generation."""
    
    def __init__(self, config: ConfigLoader, embedding_gen: EmbeddingGenerator, 
                 vector_db: VectorDatabase):
        self.config = config
        self.embedding_gen = embedding_gen
        self.vector_db = vector_db
        self.memory_monitor = MemoryMonitor(
            max_memory_mb=config.get('memory.max_memory_usage_mb', 6000)
        )
        
        self.llm_provider = config.get('llm.provider', 'template')
        self.ollama_url = config.get('llm.ollama_base_url', 'http://localhost:11434')

        self.llama_model = None
        if self.llm_provider == 'llama-cpp':
            model_path = config.get('llm.llama_cpp.model_path')
            if model_path and "UPDATE THIS PATH" not in model_path:
                try:
                    self.llama_model = Llama(
                        model_path=model_path,
                        n_ctx=config.get('llm.llama_cpp.n_ctx', 2048),
                        n_gpu_layers=config.get('llm.llama_cpp.n_gpu_layers', 0),
                        verbose=False
                    )
                    print(f"Loaded local Llama model from {model_path}")
                except Exception as e:
                    print(f"Failed to load local Llama model: {e}")
            else:
                print("Warning: Llama model path not configured in config.yaml")
    
    def query(self, query_text: str, top_k: int = 5, 
              user_role: str = 'viewer') -> Dict:
        """Process a query and return relevant results with generated response."""
        # Generate query embedding
        query_embedding = self.embedding_gen.generate_embeddings(query_text)
        
        # Search for similar documents
        results = self.vector_db.search(query_embedding, k=top_k)
        print(f"DEBUG: Vector DB found {len(results)} results for query: '{query_text}'")
        
        # Filter results based on user role (if RBAC enabled)
        if self.config.get('rbac.enabled', True):
            results = self._filter_by_role(results, user_role)
            print(f"DEBUG: After role filtering: {len(results)} results")
        
        # Generate response
        response = self._generate_response(query_text, results)
        
        return {
            'query': query_text,
            'results': results,
            'response': response,
            'result_count': len(results),
            'debug_info': {
                'vector_db_total': self.vector_db.index.ntotal,
                'vector_db_metadata_len': len(self.vector_db.metadata),
                'query_embedding_shape': query_embedding.shape,
                'query_embedding_norm': np.linalg.norm(query_embedding),
                'raw_results_count': len(results)
            }
        }
    
    def _filter_by_role(self, results: List[Dict], user_role: str) -> List[Dict]:
        """Filter results based on user role and document permissions."""
        # Simple implementation - can be extended with document-level permissions
        role_permissions = self.config.get('rbac.roles', [])
        user_perms = None
        
        for role in role_permissions:
            if role['name'] == user_role:
                user_perms = role.get('permissions', [])
                break
        
        if user_perms is None:
            return []  # No permissions
        
        # For now, all roles can see all documents
        # In production, add document-level permission checks
        return results
    
    def _generate_response(self, query: str, results: List[Dict]) -> str:
        """Generate a response using the retrieved context."""
        if not results:
            return "I couldn't find any relevant information in the knowledge base."
        
        # Build context from top results
        context_parts = []
        for i, result in enumerate(results[:3], 1):  # Use top 3 for context
            chunk_text = result.get('text', '')
            file_name = result.get('file_name', 'Unknown')
            context_parts.append(f"[Source {i} from {file_name}]: {chunk_text}")
        
        context = "\n\n".join(context_parts)
        
        # Generate response based on provider
        if self.llm_provider == 'gemini':
            return self._generate_with_gemini(query, context)
        elif self.llm_provider == 'ollama':
            return self._generate_with_ollama(query, context, results)
        elif self.llm_provider == 'llama-cpp':
            return self._generate_with_llama_cpp(query, context)
        else:
            return self._generate_template_response(query, context, results)

    def _generate_with_gemini(self, query: str, context: str) -> str:
        """Generate response using Google Gemini API."""
        api_key = self.config.get('llm.gemini_api_key')
        if not api_key:
             return "Error: Gemini API key not found in config.yaml. Please add it to use Gemini."
        
        try:
            genai.configure(api_key=api_key)
            model_name = self.config.get('llm.gemini_model', 'gemini-1.5-flash')
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""You are a helpful and accurate assistant. Use the provided context to answer the user's question.
            
Context:
{context}

Question: {query}

Instructions:
1. Answer strictly based on the provided context.
2. If the answer is not in the context, explicitly say "I cannot find the answer in the provided documents."
3. Be concise and professional.

Answer:"""
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.get('llm.temperature', 0.3),
                    max_output_tokens=self.config.get('llm.max_tokens', 1000)
                )
            )
            
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return f"Error communicating with Gemini API: {str(e)}"
    
    def _generate_with_ollama(self, query: str, context: str, results: List[Dict]) -> str:
        """Generate response using Ollama API."""
        try:
            prompt = f"""Based on the following context, answer the question. 
If the context doesn't contain enough information, say so.

Context:
{context}

Question: {query}

Answer:"""
            
            # Use 'llama3.1' as default if not specified, fallback responsibly
            model_name = self.config.get('llm.model_name', 'llama3.1')
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.get('llm.temperature', 0.7),
                        "num_predict": self.config.get('llm.max_tokens', 500)
                    }
                },
                timeout=120  # Increased timeout for local models
            )
            
            if response.status_code == 200:
                answer = response.json().get('response', '')
                if answer:
                    return answer
                else:
                    print("Ollama returned empty response.")
                    return self._generate_template_response(query, context, results)
            else:
                print(f"Ollama API error: Status {response.status_code} - {response.text}")
                return self._generate_template_response(query, context, results)
        except Exception as e:
            print(f"Ollama error: {e}. Falling back to template response.")
            return self._generate_template_response(query, context, results)
    
    def _generate_with_llama_cpp(self, query: str, context: str) -> str:
        """Generate response using local Llama 3 model via llama-cpp-python."""
        if not self.llama_model:
            return "Error: Local Llama model not loaded. Please check config.yaml path."
        
        # Llama 3 Chat Prompt Format
        prompt_with_context = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful and accurate assistant. Use the provided context to answer the user's question.
If the answer is not in the context, explicitly say "I cannot find the answer in the provided documents."
Be concise and professional.

Context:
{context}<|eot_id|><|start_header_id|>user<|end_header_id|>

{query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        try:
            output = self.llama_model(
                prompt_with_context,
                max_tokens=self.config.get('llm.llama_cpp.max_tokens', 1000),
                stop=["<|eot_id|>"],
                temperature=self.config.get('llm.llama_cpp.temperature', 0.1),
                echo=False
            )
            return output['choices'][0]['text'].strip()
        except Exception as e:
            print(f"Llama inference error: {e}")
            return f"Error generating response: {str(e)}"
    
    def _generate_template_response(self, query: str, context: str, 
                                   results: List[Dict]) -> str:
        """Generate a template-based response (no LLM required)."""
        if not results:
            return "I couldn't find any relevant information in the knowledge base."
        
        # Create a simple template response
        response_parts = [
            f"Based on the knowledge base, here's what I found regarding '{query}':\n\n"
        ]
        
        for i, result in enumerate(results[:3], 1):
            score = result.get('score', 0)
            text = result.get('text', '')[:300]  # Limit length
            file_name = result.get('file_name', 'Unknown')
            
            response_parts.append(
                f"**Relevant excerpt {i}** (from {file_name}, relevance: {score:.2f}):\n"
                f"{text}...\n"
            )
        
        response_parts.append(
            "\nFor more details, please refer to the source documents listed above."
        )
        
        return "\n".join(response_parts)



