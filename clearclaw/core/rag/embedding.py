"""
向量化服务 - 默认使用通义千问Embedding模型
"""

import os
from typing import List, Optional
from dashscope import TextEmbedding
from dotenv import load_dotenv
load_dotenv()


class QwenEmbedding:
    """
    通义千问Embedding服务（阿里云百炼）

    固定使用: text-embedding-v3
    文档: https://help.aliyun.com/zh/dashscope/developer-reference/text-embedding-api
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-v3",
    ):
        self.api_key = api_key or os.getenv("QWEN_EMBEDDING_API_KEY")
        if not self.api_key:
            raise ValueError("请设置环境变量：QWEN_EMBEDDING_API_KEY")

        self.model = model

    def embed_query(self, text: str) -> List[float]:
        """将单个文本向量化"""
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量向量化（支持最多10条/次）"""
        if not texts:
            return []

        # dashscope单次最多10条，再多报错
        batch_size = 10
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            resp = TextEmbedding.call(
                model=self.model,
                input=batch,
                api_key=self.api_key,
            )

            if resp.status_code != 200:
                raise RuntimeError(
                    f"通义千问Embedding API调用失败: "
                    f"status={resp.status_code}, message={resp.message}"
                )

            # 按原始顺序提取向量
            # resp.output['embeddings']是一个列表，每个元素有'embedding'字段
            embeddings = [item["embedding"] for item in resp.output["embeddings"]]
            all_embeddings.extend(embeddings)

        return all_embeddings


# 全局单例
_embedding_instance = None


def get_embedding() -> QwenEmbedding:
    """获取Embedding单例"""
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = QwenEmbedding()
    return _embedding_instance