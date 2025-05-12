import faiss
from llama_index.core import (
    SimpleDirectoryReader,
    load_index_from_storage,
    VectorStoreIndex,
    StorageContext,
)
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

documents = SimpleDirectoryReader(input_dir="./retrieval/long_memory/data").load_data()

dimension = 384
faiss_index = faiss.IndexFlatIP(dimension)

vector_store = FaissVectorStore(faiss_index=faiss_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context,embed_model=embed_model
)

# save index to disk
index.storage_context.persist()