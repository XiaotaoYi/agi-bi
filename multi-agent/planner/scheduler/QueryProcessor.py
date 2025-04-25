import sqlite3
import requests
import json
from typing import Optional
import re
import os
from retrieval.long_memory.sql_util import SQLVectorDB

class SQLProcessor:
    def __init__(self, db_path: str, ollama_endpoint: str = "http://localhost:11434/api/generate"):
        """
        初始化数据库处理器
        :param db_path: SQLite数据库文件路径
        :param ollama_endpoint: Ollama API端点地址
        """
        self.db_path = db_path
        self.ollama_endpoint = ollama_endpoint
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 启用行工厂获取字典格式结果
        self.sql_vector_db = SQLVectorDB() 

    def _call_deepseek(self, prompt: str, format_instruction: Optional[str] = None) -> str:
        """
        封装调用DeepSeek模型的私有方法
        :param prompt: 输入提示
        :param format_instruction: 可选的结果格式指令
        :return: 模型生成的响应
        """
        full_prompt = f"{prompt}\n{format_instruction}" if format_instruction else prompt
        print('full prompt:' + full_prompt)
        
        payload = {
            "model": "deepseek-r1:14B",
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": 0.2}
        }

        try:
            response = requests.post(
                self.ollama_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()
            return json.loads(response.text)["response"]
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"模型调用失败: {str(e)}")

    def _execute_sql(self, sql: str) -> list:
        """
        执行SQL查询并返回结果
        :param sql: 要执行的SQL语句
        :return: 查询结果列表
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            
            if sql.strip().lower().startswith("select"):
                results = [dict(row) for row in cursor.fetchall()]
                print("\n原始执行结果：")
                for idx, row in enumerate(results, 1):
                    print(f"{idx}. {dict(row)}")
                return results
            else:
                self.conn.commit()
                return [{"affected_rows": cursor.rowcount}]
                
        except sqlite3.Error as e:
            raise RuntimeError(f"SQL执行错误: {str(e)}")

    def _format_results(self, results: list, original_query: str) -> str:
        """
        使用DeepSeek美化查询结果
        :param results: SQL执行结果
        :param original_query: 原始用户查询
        :return: 美化后的自然语言描述
        """
        format_instruction = """
        请将以下JSON格式的SQL查询结果转换为自然语言描述，无需显示自然语言字样，要求回答简洁
        保持专业且易于理解的风格，使用中文输出，
        并保留关键数据细节。原始用户查询是：{query}
        """.format(query=original_query)

        return self._call_deepseek(
            prompt=json.dumps(results, ensure_ascii=False),
            format_instruction=format_instruction
        )

    def get_query_examples(self, query: str):
        return self.sql_vector_db.search(query)

    def process(self, query: str):
        """
        处理用户查询的完整流程
        :param query: 自然语言查询
        """
        results = {}
        try:
            # 第一步：生成SQL语句
            sql_prompt = f"""
            请根据以下查询生成SQL语句（仅返回SQL代码，不要输出think内容）：
            数据库Schema：{self._get_schema_info()}
            用户查询：{query}
            以下为用户查询和生成的SQL样例：
            {self.get_query_examples(query)}
            """
            generated_sql = self._call_deepseek(sql_prompt).strip().replace("```sql", "").replace("```", "")

            print(f"生成的SQL语句：\n{generated_sql}")

            # 使用正则表达式替换 <think> 标签及其内容，以及换行符
            cleaned_text = re.sub(r'<think>.*?</think>', '', generated_sql, flags=re.DOTALL)  # 替换 <think> 标签及其内容

            print(cleaned_text)

            # 第二步：验证SQL语法并执行
            from sqlite_verify import parse_sql
            
            # 验证SQL语法是否正确
            if parse_sql(cleaned_text):
                # SQL语法正确，执行SQL
                results = self._execute_sql(cleaned_text)
            else:
                # SQL语法不正确，返回错误信息
                print("SQL语法验证失败")
                results = [{"error": "当前系统正在繁忙，请稍后再试"}]

            # 第三步：美化输出
            #formatted_output = self._format_results(results, query)
            #print("\n美化后的解释：")
            #print(formatted_output)

        except Exception as e:
            print(f"处理过程中发生错误：{str(e)}")
        
        return results

    def _get_schema_info(self) -> str:
        """
        获取数据库schema信息用于提示工程
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        return "\n".join([f"{table[0]}表结构：{table[1]}" for table in cursor.fetchall()])

    def __del__(self):
        """确保数据库连接关闭"""
        if hasattr(self, 'conn'):
            self.conn.close()

# 使用示例
if __name__ == "__main__":
    processor = SQLProcessor("order.db")
    user_query = "请帮我查询8月份消费金额最高的前三位用户"
    processor.process(user_query)