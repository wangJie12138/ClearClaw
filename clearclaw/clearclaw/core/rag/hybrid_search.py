from typing import List, Tuple
import jieba
from rank_bm25 import BM25Okapi


class HybridSearcher:
    def __init__(self, vector_db, documents: List[str]):
        self.vector_db = vector_db
        # 准备BM25
        tokenized_docs = [list(jieba.cut(doc)) for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        self.documents = documents

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, dict]]:
        # 向量检索
        print(f"向量检索中... (top_k * 2 = {top_k * 2})")
        vector_results = self.vector_db.search(query, top_k * 2)
        print(f"向量检索返回 {len(vector_results)} 条结果")

        # 关键词检索(BM25)
        print(f"BM25 检索中...")
        tokenized_query = list(jieba.cut(query))
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_results = sorted(
            [(self.documents[i], score) for i, score in enumerate(bm25_scores)],
            key=lambda x: x[1],
            reverse=True
        )[:top_k * 2]
        print(f"BM25 返回 {len(bm25_results)} 条结果")

        # RRF融合
        final = reciprocal_rank_fusion(vector_results, bm25_results, top_k)
        return final


def reciprocal_rank_fusion(vec_results, bm25_results, k=60, top_n=5):
    """RRF融合(倒数排名融合)，保留meta"""
    scores = {}

    # 收集每个文档的meta（从向量结果中取）
    doc_meta = {}
    for doc, score, meta in vec_results:
        doc_meta[doc] = meta

    # 计算 RRF 分数
    for rank, (doc, score, meta) in enumerate(vec_results):
        scores[doc] = scores.get(doc, 0) + 1 / (k + rank + 1)

    for rank, (doc, score) in enumerate(bm25_results):
        scores[doc] = scores.get(doc, 0) + 1 / (k + rank + 1)

    # 排序并返回 (doc, score, meta)
    sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    final = []
    for doc, rrf_score in sorted_results[:top_n]:
        meta = doc_meta.get(doc, {})  # 从向量结果中取meta
        final.append((doc, rrf_score, meta))

    return final