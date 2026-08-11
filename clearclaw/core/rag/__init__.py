"""
ClearClaw RAG模块

提供文档索引、向量检索、混合检索、重排序等能力
"""

from .embedding import QwenEmbedding, get_embedding
from .vector_store import VectorDB
from .retriever import search_knowledge, ensure_indexed, load_documents

__all__ = [
    "QwenEmbedding",
    "get_embedding",
    "VectorDB",
    "search_knowledge",
    "load_documents",
    "ensure_indexed",
]

