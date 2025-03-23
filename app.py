from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from QueryProcessor import SQLProcessor
import os
import re

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # 启用跨域请求支持

# 初始化数据库处理器
db_path = "order.db"  # 使用您的数据库路径
processor = SQLProcessor(db_path)

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def process_query():
    """处理用户查询的API端点"""
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': '查询不能为空'}), 400
    
    try:
        # 使用处理器处理查询并捕获结果
        import io
        import sys
        
        # 捕获标准输出
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        
        # 处理查询
        processor.process(query)
        
        # 恢复标准输出并获取捕获的输出
        sys.stdout = old_stdout
        output = new_stdout.getvalue()
        # 使用正则表达式替换 <think> 标签及其内容，以及换行符
        output = re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL)  # 替换 <think> 标签及其内容

        print(output)
        
        # 解析输出以获取SQL和结果
        sql_match = output.split("生成的SQL语句：\n")[1].split("\n原始执行结果：")[0] if "生成的SQL语句：" in output else ""
        result = output.split("\n美化后的解释：\n")[1] if "\n美化后的解释：\n" in output else output
        
        return jsonify({
            'result': result.strip()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8082) 