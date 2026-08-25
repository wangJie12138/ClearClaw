
'''
test: 查看向量数据库数据
'''

from pathlib import Path

import sqlite3

db_path = Path(r"/ClearClaw/clearclaw/core/workspace/vector_db/chroma.sqlite3")
if not db_path.exists():
    print(f"找不到数据库文件: {db_path}")
    exit()

print(f"找到数据库: {db_path}\n")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# 1. 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("数据库中的表:")
for table in tables:
    print(f"   {table[0]}")

print("\n" + "=" * 60)

# 2. 查看关键表的结构和数据量
key_tables = ['segments', 'embeddings', 'collections', 'embedding_metadata']
for table_name in key_tables:
    if table_name not in [t[0] for t in tables]:
        continue

    print(f"\n表: {table_name}")

    # 查看列
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]
    print(f"   列: {', '.join(col_names)}")

    # 记录数
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"   记录数: {count}")

    # 如果有数据，显示前3条
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        for i, row in enumerate(rows):
            print(f"   样例 {i + 1}: {row}")

print("\n" + "=" * 60)

# 3. 总结
cursor.execute("SELECT COUNT(*) FROM segments")
seg_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM embeddings")
emb_count = cursor.fetchone()[0]

cursor.execute("SELECT id, name, dimension FROM collections")
rows = cursor.fetchall()
print("\ncollections 表:")
for row in rows:
    print(f"   ID: {row[0]}, Name: {row[1]}, Dimension: {row[2]}")

print(f"\n总结:")
print(f"   segments 表记录数: {seg_count}")
print(f"   embeddings 表记录数: {emb_count}")

if seg_count == 0 and emb_count == 0:
    print("   !!!知识库为空，没有任何数据被索引。")
else:
    print("   知识库中有数据，RAG 应该可以工作。")


conn.close()