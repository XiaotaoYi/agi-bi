import re

# 假设文件内容已经存储在变量 text 中
# 1. 加载 txt 文件
file_path = 'data/wallStreatWeek/WallStreetWeek20250314.txt'  # 替换为你的文件路径
with open(file_path, 'r', encoding='utf-8') as file:
    text = file.read()

# 1. 转换为小写
text = text.lower()

# 2. 去除标点符号和特殊字符
text = re.sub(r'[^\w\s]', '', text)

# 3. 分割成单词列表
words = text.split()

# 4. 使用集合去重
unique_words = set(words)

# 5. 计算不重复单词的数量
unique_word_count = len(unique_words)

print(f"不重复单词的数量: {unique_word_count}")

print(unique_words)