import sqlite3
import random
from datetime import datetime, timedelta


def insertData():
    # 创建数据库连接
    conn = sqlite3.connect('semantic/glossary/glossary.db')
    c = conn.cursor()

    # 创建带注释的user表
    c.execute('''
    CREATE TABLE if not exists glossary_tbl  (
        id INTEGER PRIMARY KEY,                                       -- identity of user
        abbr STRING,                                                  -- gender of user
        fullname STRING,                                              -- age of user
        description STRING                                            -- level of customer account
    )''')

    # 生成1条glossary数据
    records = []
    records.append((1,'GMV','Gross Merchandise Volume','gross transaction amount of a specified time range'))
    records.append((2,'tpv','total payment volume','total payment volume'))

    # 插入数据
    c.executemany('INSERT INTO "glossary_tbl" VALUES (?,?,?,?)', records)

    # 提交并关闭
    conn.commit()
    conn.close()

def list():
    # 创建数据库连接
    conn = sqlite3.connect('semantic/glossary/glossary.db')
    c = conn.cursor()
    c.execute('select * from glossary_tbl')
    print(c.fetchall())
    conn.close()

insertData()
list()

