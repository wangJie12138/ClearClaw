"""
向量存储 - 基于Chroma
"""
import hashlib
import traceback
from pathlib import Path
from typing import List, Tuple, Optional

import chromadb
from chromadb.config import Settings

from .embedding import get_embedding


class VectorDB:
    """向量数据库"""

    def __init__(self, persist_dir: Optional[str] = None):
        stack_trace = ''.join(traceback.format_stack()[:-1])
        if "get_db()" not in stack_trace:
            print("【1】调用栈信息：\n", stack_trace)

        # 使用绝对路径
        if persist_dir is None:
            # 当前vector_db.py文件所在目录向上推导 workspace
            base_dir = Path(__file__).parent.parent
            persist_dir = str(base_dir / "workspace" / "vector_db")

        self.persist_dir = persist_dir
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        print(f"【2】持久化绝对路径: {Path(self.persist_dir).resolve()}")

        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
        print("【3】Chroma 客户端已初始化")

        self.embedding = get_embedding()
        print("【4】Embedding 已加载")

        self.collection = self._get_or_create()
        print(f"【5】集合已获取/创建: {self.collection.name}")

    def _get_or_create(self):
        """存在则获取，不存在新建，不会删除已有集合"""
        return self.client.get_or_create_collection("knowledge")

    def add(self, chunks: List[dict], batch_size: int = 50):
        """批量添加向量（使用upsert，重复ID自动覆盖）"""
        if not chunks:
            return

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c["content"] for c in batch]
            ids = [hashlib.md5(t.encode("utf-8")).hexdigest()[:16] for t in texts]
            metadatas = [{"source": c["source"]} for c in batch]

            try:
                embeddings = self.embedding.embed_documents(texts)
            except Exception as e:
                print(f"!!!向量化失败: {e}")
                raise

            try:
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                )
                print(f"已索引 {min(i + batch_size, len(chunks))}/{len(chunks)}")
            except Exception as e:
                print(f"!!!写入Chroma失败: {e}")
                raise

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, dict]]:
        """检索向量，返回 (文本, 相似度, metadata)"""
        query_vec = self.embedding.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_vec],
            n_results=top_k,
            include=["documents", "distances", "metadatas"],
        )

        if not results["documents"] or not results["documents"][0]:
            return []

        return [
            (results["documents"][0][i], 1.0 - results["distances"][0][i], results["metadatas"][0][i])
            for i in range(len(results["documents"][0]))
        ]

    def count(self) -> int:
        """获取文档总数"""
        return self.collection.count()

    def clear(self):
        """清空知识库"""
        try:
            self.client.delete_collection("knowledge")
        except chromadb.errors.NotFoundError:
            pass
        self.collection = self._get_or_create()


_db_instance: Optional[VectorDB] = None


def get_db() -> VectorDB:
    """全局单例入口，项目只能通过此函数获取VectorDB实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = VectorDB()
    return _db_instance