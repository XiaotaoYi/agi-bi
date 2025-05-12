import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json

# 1. 初始化模型
model = SentenceTransformer('BAAI/bge-m3', trust_remote_code=True)

# 2. 示例数据集
path = "retrieval/long_memory/samples.json"
with open(path, "r") as f:
    dataset = json.load(f)
documents = dataset

queries = [
    "search tpv at the year 2024 by month"
]

# 3. 生成向量表示
doc_embeddings = model.encode(documents, normalize_embeddings=True)  # 归一化
query_embeddings = model.encode(queries, normalize_embeddings=True)

# 4. 构建 FAISS 索引
dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)  # 内积相似度
index.add(doc_embeddings)

# 5. 使用 FAISS 初步检索
k = 5  # 初始检索 top-k
D, I = index.search(query_embeddings, k)

# 6. 使用 BGE-M3 重排序
top_k = 5  # 最终保留的 top-k 结果
reranked_results = []

for idx, query in enumerate(queries):
    # 提取 FAISS 返回的候选文档
    candidates = [documents[i] for i in I[idx]]
    
    # 生成候选文档的嵌入向量
    candidate_embeddings = model.encode(candidates, normalize_embeddings=True)
    
    # 计算当前查询与候选文档的相似度
    # 使用点积（因为向量已归一化，点积 = 余弦相似度）
    scores = np.dot(query_embeddings[idx].reshape(1, -1), candidate_embeddings.T).flatten()
    
    # 合并并排序
    results = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:top_k]
    reranked_results.append(results)

# 7. 输出结果
for i, (query, results) in enumerate(zip(queries, reranked_results)):
    print(f"\nQuery {i+1}: {query}")
    print("Reranked Results:")
    for j, (doc, score) in enumerate(results):
        print(f"  {j+1}. {doc} (Score: {score:.4f})")