import re
import sqlparse
from collections import defaultdict

def parse_sql(query):
    """解析SQL查询，提取关键特征"""
    query = re.sub(r'\s+', ' ', query).lower()  # 统一格式化
    parsed = sqlparse.parse(query)[0]
    
    # 提取操作类型（SELECT/UPDATE等）
    operation = parsed.get_type().upper()
    
    # 提取表名（FROM/JOIN子句）
    tables = set()
    from_seen = False
    for token in parsed.tokens:
        if isinstance(token, sqlparse.sql.Token) and token.value.upper() in ('FROM', 'JOIN'):
            from_seen = True
            continue
        if from_seen and isinstance(token, sqlparse.sql.Identifier):
            tables.add(token.get_real_name())
            from_seen = False
    
    # 提取字段名（SELECT和GROUP BY子句）
    columns = set()
    group_by_fields = []
    for idx, token in enumerate(parsed.tokens):
        if isinstance(token, sqlparse.sql.IdentifierList):
            for identifier in token.get_identifiers():
                columns.add(identifier.get_real_name())
        elif token.ttype == sqlparse.tokens.Keyword and token.value.upper() == 'GROUP BY':
            # 获取 GROUP BY 后的下一个 token（使用索引 idx）
            _, next_token = parsed.token_next(idx)  # 此处传入索引 idx，而非 token 对象

            # 提取所有字段（处理逗号分隔的多个字段）
            if next_token:
                # 使用 sqlparse 的 IdentifierList 分割字段
                if isinstance(next_token, sqlparse.sql.IdentifierList):
                    for identifier in next_token.get_identifiers():
                        # 提取原始字段名（去除别名和表名前缀）
                        field = identifier.get_real_name()
                        group_by_fields.append(field)
                # 处理单个字段的情况
                elif isinstance(next_token, sqlparse.sql.Identifier):
                    field = next_token.get_real_name()
                    group_by_fields.append(field)
    
    return {
        "operation": operation,
        "tables": list(tables),
        "columns": list(columns),
        "group_by": group_by_fields
    }

# 示例SQL日志
queries = [
    "SELECT user_id, COUNT(*) FROM orders WHERE dt='2023-10-01' GROUP BY user_id;",
    "SELECT product_id, SUM(amount) FROM sales GROUP BY product_id;",
    "SELECT user_id, product_id, SUM(amount) FROM sales GROUP BY user_id, product_id;"
]

# 提取所有查询的特征
features_list = [parse_sql(q) for q in queries]

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import pandas as pd

# 将查询特征转化为文本（用于TF-IDF）
def feature_to_text(feature):
    return ' '.join([
        f"operation_{feature['operation']}",
        *[f"table_{t}" for t in feature['tables']],
        *[f"column_{c}" for c in feature['columns']],
        *[f"groupby_{g}" for g in feature['group_by']]
    ])

# 生成TF-IDF向量
texts = [feature_to_text(f) for f in features_list]
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

# 使用DBSCAN聚类
clustering = DBSCAN(eps=0.5, min_samples=1).fit(X.toarray())
labels = clustering.labels_

# 统计高频簇
df = pd.DataFrame({"query": queries, "cluster": labels})
cluster_counts = df["cluster"].value_counts()
top_clusters = cluster_counts.head(2).index.tolist()  # 取前2个高频簇

def generate_materialized_view(cluster_queries):
    # 提取所有查询的特征
    features = [parse_sql(q) for q in cluster_queries]
    
    # 统计公共元素
    common_tables = list(set.intersection(*[set(f["tables"]) for f in features]))
    common_group_by = list(set.intersection(*[set(f["group_by"]) for f in features]))
    
    # 确定聚合字段（假设所有查询使用相同的聚合函数）
    agg_columns = defaultdict(list)
    for f in features:
        for col in f["columns"]:
            if col not in common_group_by:
                agg_columns[col].append(col)
    
    # 选择高频聚合字段（示例取第一个）
    agg_field = list(agg_columns.keys())[0] if agg_columns else None
    
    # 生成物化视图DDL
    if common_tables and common_group_by and agg_field:
        table_name = common_tables[0]
        mv_name = f"mv_{table_name}_{'_'.join(common_group_by)}"
        ddl = f"""
        CREATE MATERIALIZED VIEW {mv_name}
        AS
        SELECT
            {', '.join(common_group_by)},
            SUM({agg_field}) AS total_{agg_field}
        FROM {table_name}
        GROUP BY {', '.join(common_group_by)};
        """
        return ddl
    return None

# 为每个高频簇生成物化视图
for cluster_id in top_clusters:
    cluster_queries = df[df["cluster"] == cluster_id]["query"].tolist()
    ddl = generate_materialized_view(cluster_queries)
    if ddl:
        print(f"Cluster {cluster_id} 生成的物化视图:\n{ddl}")