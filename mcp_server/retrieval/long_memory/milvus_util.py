import json

from pymilvus import (
    MilvusClient,
    DataType,
    Function,
    FunctionType,
    AnnSearchRequest,
    RRFRanker,
)

from pymilvus.model.hybrid import BGEM3EmbeddingFunction


class HybridRetriever:
    def __init__(self, uri, collection_name="hybrid", dense_embedding_function=None):
        self.uri = uri
        self.collection_name = collection_name
        self.embedding_function = dense_embedding_function
        self.use_reranker = True
        self.use_sparse = True
        self.client = MilvusClient(uri=uri)

    def build_collection(self):
        if isinstance(self.embedding_function.dim, dict):
            dense_dim = self.embedding_function.dim["dense"]
        else:
            dense_dim = self.embedding_function.dim

        tokenizer_params = {
            "tokenizer": "standard",
            "filter": [
                "lowercase",
                {
                    "type": "length",
                    "max": 200,
                },
                {"type": "stemmer", "language": "english"},
                {
                    "type": "stop",
                    "stop_words": [
                        "a",
                        "an",
                        "and",
                        "are",
                        "as",
                        "at",
                        "be",
                        "but",
                        "by",
                        "for",
                        "if",
                        "in",
                        "into",
                        "is",
                        "it",
                        "no",
                        "not",
                        "of",
                        "on",
                        "or",
                        "such",
                        "that",
                        "the",
                        "their",
                        "then",
                        "there",
                        "these",
                        "they",
                        "this",
                        "to",
                        "was",
                        "will",
                        "with",
                    ],
                },
            ],
        }

        schema = MilvusClient.create_schema()
        schema.add_field(
            field_name="pk",
            datatype=DataType.VARCHAR,
            is_primary=True,
            auto_id=True,
            max_length=100,
        )
        schema.add_field(
            field_name="content",
            datatype=DataType.VARCHAR,
            max_length=65535,
            analyzer_params=tokenizer_params,
            enable_match=True,
            enable_analyzer=True,
        )
        schema.add_field(
            field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR
        )
        schema.add_field(
            field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=dense_dim
        )

        functions = Function(
            name="bm25",
            function_type=FunctionType.BM25,
            input_field_names=["content"],
            output_field_names="sparse_vector",
        )

        schema.add_function(functions)

        index_params = MilvusClient.prepare_index_params()
        index_params.add_index(
            field_name="sparse_vector",
            index_type="SPARSE_INVERTED_INDEX",
            metric_type="BM25",
        )
        index_params.add_index(
            field_name="dense_vector", index_type="FLAT", metric_type="IP"
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params,
        )

    def insert_data(self, chunk, metadata):
        embedding = self.embedding_function([chunk])
        if isinstance(embedding, dict) and "dense" in embedding:
            dense_vec = embedding["dense"][0]
        else:
            dense_vec = embedding[0]
        self.client.insert(
            self.collection_name, {"dense_vector": dense_vec, **metadata}
        )

    def search(self, query: str, k: int = 20, mode="hybrid"):

        output_fields = [
            "content"
        ]
        if mode in ["dense", "hybrid"]:
            embedding = self.embedding_function([query])
            if isinstance(embedding, dict) and "dense" in embedding:
                dense_vec = embedding["dense"][0]
            else:
                dense_vec = embedding[0]

        if mode == "sparse":
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query],
                anns_field="sparse_vector",
                limit=k,
                output_fields=output_fields,
            )
        elif mode == "dense":
            results = self.client.search(
                collection_name=self.collection_name,
                data=[dense_vec],
                anns_field="dense_vector",
                limit=k,
                output_fields=output_fields,
            )
        elif mode == "hybrid":
            full_text_search_params = {"metric_type": "BM25"}
            full_text_search_req = AnnSearchRequest(
                [query], "sparse_vector", full_text_search_params, limit=k
            )

            dense_search_params = {"metric_type": "IP"}
            dense_req = AnnSearchRequest(
                [dense_vec], "dense_vector", dense_search_params, limit=k
            )

            results = self.client.hybrid_search(
                self.collection_name,
                [full_text_search_req, dense_req],
                ranker=RRFRanker(),
                limit=k,
                output_fields=output_fields,
            )
        else:
            raise ValueError("Invalid mode")
        return [
            {
                "content": doc["entity"]["content"]
            }
            for doc in results[0]
        ]


dense_ef = BGEM3EmbeddingFunction()
standard_retriever = HybridRetriever(
    uri="http://localhost:19530",
    collection_name="milvus_hybrid4",
    dense_embedding_function=dense_ef,
)

path = "retrieval/long_memory/samples.json"
with open(path, "r") as f:
    dataset = json.load(f)

is_insert = False
if is_insert:
    standard_retriever.build_collection()
    for doc in dataset:
        doc_content = doc['question']
        metadata = {
                "content": doc_content
            }
        standard_retriever.insert_data(doc_content, metadata)
user_query = 'Find tpv for cross-border transactions today'
raw_results = standard_retriever.search("Find tpv for cross-border transactions today", mode="hybrid", k=10)

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from pymilvus import connections, Collection
# 2. 加载 BGE-M3 Rerank 模型
def load_rerank_model():
    model_name = "BAAI/bge-m3"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    if torch.cuda.is_available():
        model = model.cuda()
    return tokenizer, model

# 3. 执行 Rerank
def rerank_results(query, raw_results, tokenizer, model, top_k=10):
    # 准备输入对
    pairs = [(query, item["content"]) for item in raw_results]
    
    # 使用 SentenceTransformer 的 encode 方法获取嵌入
    query_embedding = model.encode(query, convert_to_tensor=True)
    doc_embeddings = model.encode([item["content"] for item in raw_results], convert_to_tensor=True)
    
    # 计算余弦相似度
    scores = torch.nn.functional.cosine_similarity(
        query_embedding.unsqueeze(0),
        doc_embeddings
    ).cpu().numpy()
    
    # 合并分数并排序
    for i, item in enumerate(raw_results):
        item["rerank_score"] = float(scores[i])
    
    # 按 rerank 分数降序排序
    reranked = sorted(raw_results, key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]

# Step 2: 加载 rerank 模型
tokenizer, model = load_rerank_model()

# Step 3: 执行重排序
final_results = rerank_results(user_query, raw_results, tokenizer, model)

# 打印结果
print("原始排序 | 重排序后")
print("-----------------------")
for i, item in enumerate(raw_results):
    print(f"内容: {item['content']}...")