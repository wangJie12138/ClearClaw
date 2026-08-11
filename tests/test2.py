'''
test: 删除持久化会话
'''


from pathlib import Path
import chromadb
from chromadb.config import Settings

path = Path("../clearclaw/core/workspace/vector_db").resolve()
client = chromadb.PersistentClient(path=str(path), settings=Settings(anonymized_telemetry=False))

try:
    client.delete_collection("knowledge")
    print("✅ knowledge 集合已删除")
except Exception as e:
    print(f"集合不存在：{e}")