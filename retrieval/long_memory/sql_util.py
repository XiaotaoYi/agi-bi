import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

class SQLVectorDB:
    def __init__(self, index_path='faiss_index.bin'):
        self.model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
        self.index_path = index_path
        self.examples = []
        
        # Try to load existing index
        if os.path.exists(index_path):
            try:
                self.index = faiss.read_index(index_path)
                # Load examples from the saved file
                examples_path = index_path + '.examples'
                if os.path.exists(examples_path):
                    with open(examples_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                query, sql = line.strip().split('：')
                                self.examples.append((query, sql))
            except Exception as e:
                print(f"Error loading index: {e}")
                self.index = None
        else:
            self.index = None
        
    def import_data(self, file_path):
        """Import data from example_data.txt and create FAISS index"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")
            
        # Read examples
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Parse examples
        for line in lines:
            if line.strip():
                query, sql = line.strip().split('：')
                self.examples.append((query, sql))
                
        # Vectorize queries
        queries = [example[0] for example in self.examples]
        embeddings = self.model.encode(queries, normalize_embeddings=True)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings.astype('float32'))
        
        # Save index and examples
        self._save_index()
        
    def _save_index(self):
        """Save the FAISS index and examples to disk"""
        if self.index is not None:
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Save examples
            examples_path = self.index_path + '.examples'
            with open(examples_path, 'w', encoding='utf-8') as f:
                for query, sql in self.examples:
                    f.write(f"{query}：{sql}\n")
        
    def search(self, query, k=3):
        """Search for similar queries and return corresponding SQLs"""
        if self.index is None:
            raise ValueError("Index not initialized. Please call import_data first.")
            
        # Vectorize query
        query_embedding = self.model.encode([query], normalize_embeddings=True)
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Return results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # Valid index
                results.append({
                    'query': self.examples[idx][0],
                    'sql': self.examples[idx][1],
                    'similarity': float(distances[0][i])
                })
                
        return results

# Example usage
if __name__ == "__main__":
    # Initialize vector database
    db = SQLVectorDB()
    
    # Import data
    db.import_data('faiss_index.bin.examples')
    
    # Example search
    query = "查询2025年2月份的销售情况"
    results = db.search(query)
    
    print(f"Query: {query}")
    print("\nSimilar examples:")
    for result in results:
        print(f"\nSimilarity: {result['similarity']:.4f}")
        print(f"Example query: {result['query']}")
        print(f"SQL: {result['sql']}") 