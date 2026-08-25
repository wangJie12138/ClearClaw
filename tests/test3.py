'''
test: 查看持久化会话数据
'''

import sqlite3
import os

DB_PATH = "/clearclaw/workspace/state.sqlite3"

def inspect_sqlite():
    if not os.path.exists(DB_PATH):
        print(f"文件不存在：{DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 查询所有数据表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    all_tables = cursor.fetchall()
    print("===== 数据库内所有表 =====")
    if all_tables:
        for t in all_tables:
            print(t[0])
    else:
        print("【警告】库中没有任何数据表！")

    # 2. 如果存在 checkpoints / writes，查询内容
    table_names = {t[0] for t in all_tables}
    if "checkpoints" in table_names:
        print("\n===== checkpoints 表数据 =====")
        cursor.execute("SELECT * FROM checkpoints LIMIT 20;")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        print("字段：", cols)
        for r in rows:
            print(r)

    if "writes" in table_names:
        print("\n===== writes 表数据 =====")
        cursor.execute("SELECT * FROM writes LIMIT 20;")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        print("字段：", cols)
        for r in rows:
            print(r)

    conn.close()
    print("\n查询完成")

if __name__ == "__main__":
    inspect_sqlite()