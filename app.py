from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from controller.QueryProcessor import SQLProcessor
import os
import re

app = Flask(__name__, static_folder='visualization/static', template_folder='visualization/templates')
CORS(app)  # 启用跨域请求支持

# 初始化数据库处理器
db_path = "tools/sql_executor/order.db"  # 使用您的数据库路径
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
        # 处理查询
        results = processor.process(query)
        
        return jsonify({
            'result': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 