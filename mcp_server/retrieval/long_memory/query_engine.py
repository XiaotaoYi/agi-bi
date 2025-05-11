# 步骤 6: 查询 FAISS 索引
# 加载已保存的 FAISS 索引（如果之前已保存）
# faiss_index = faiss.read_index("faiss_index.bin")
# vector_store = FaissVectorStore(faiss_index=faiss_index)

# 创建查询引擎
query_engine = index.as_query_engine(similarity_top_k=3)  # 返回最相似的 3 个结果

# 执行查询
query = "What are the benefits of having a dog?"
response = query_engine.query(query)
# 输出结果
print(response)