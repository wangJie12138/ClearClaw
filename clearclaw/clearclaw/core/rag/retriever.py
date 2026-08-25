"""
索引 + 检索（业务逻辑）
"""

import os
import hashlib
import pickle
from pathlib import Path
from typing import List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader

from .hybrid_search import HybridSearcher
from .vector_store import get_db

from pathlib import Path

# 当前retriever.py文件
THIS_FILE = Path(__file__).resolve()
# core目录
CORE_DIR = THIS_FILE.parent
# core的上级：clearclaw
CLEARCLAW_ROOT = CORE_DIR.parent
# 知识库目录（外层workspace）
DEFAULT_KNOWLEDGE_DIR = CLEARCLAW_ROOT / "workspace" / "knowledge"


# 支持的文档格式
LOADERS = {
    ".txt": TextLoader,
    ".md": TextLoader,
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
}

# 自动索引缓存
CACHE_FILE = "./workspace/.rag_index_cache.pkl"


def _get_dir_hash(directory: str) -> str:
    """计算目录下所有文件的内容哈希（检测变化）"""
    hasher = hashlib.sha256()
    for file_path in sorted(Path(directory).rglob("*")):
        if file_path.is_file():
            try:
                with open(file_path, "rb") as f:
                    hasher.update(file_path.name.encode())
                    hasher.update(f.read())
            except:
                pass
    return hasher.hexdigest()


def _is_indexed(directory: str) -> bool:
    """检查目录是否已经被索引"""
    current_hash = _get_dir_hash(directory)

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                cached_hash = pickle.load(f)
                return cached_hash == current_hash
        except:
            pass

    return False


def _mark_indexed(directory: str):
    """标记目录已索引"""
    current_hash = _get_dir_hash(directory)
    Path(os.path.dirname(CACHE_FILE)).mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(current_hash, f)


def ensure_indexed(directory: str = DEFAULT_KNOWLEDGE_DIR) -> bool:
    """
    自动索引：如果目录有变化或有新文档，自动索引。
    返回True表示索引了，False表示没有变化。
    """
    if not os.path.exists(directory):
        print(f"知识库目录不存在，跳过索引: {directory}")
        return False

    # 检查是否已索引
    if _is_indexed(directory):
        print(f"知识库已是最新，无需重新索引")
        return False

    print(f"检测到知识库变化，开始自动索引...")

    # 执行索引
    count = index_knowledge(directory)

    if count > 0:
        _mark_indexed(directory)
        print(f"自动索引完成: {count}个分块")
    else:
        print(f"未找到可索引的文档")

    return count > 0

def load_documents(directory: str) -> List[dict]:
    """加载目录下所有文档并分块"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=60,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],
    )

    all_chunks = []
    total_find_file = 0

    for ext, loader_cls in LOADERS.items():
        # 查找文件
        file_list = list(Path(directory).glob(f"**/*{ext}"))
        print(f"[扫描] 后缀{ext}找到文件数量：{len(file_list)}")
        total_find_file += len(file_list)

        for file_path in file_list:
            print(f"找到文件：{file_path}")
            try:
                docs = loader_cls(str(file_path)).load()
                chunks = splitter.split_documents(docs)

                for chunk in chunks:
                    txt = chunk.page_content.strip()
                    if not txt:
                        continue
                    all_chunks.append({
                        "content": txt,
                        "source": file_path.name,
                    })
                print(f"{file_path.name} → {len(chunks)}个分块")

            except Exception as e:
                print(f"{file_path.name}读取异常: {e}")

    print(f"[汇总] 一共扫描到文件：{total_find_file}")
    print(f"[汇总] 有效文本块总数：{len(all_chunks)}")
    return all_chunks


def index_knowledge(directory: str) -> int:
    """一键索引知识库"""
    chunks = load_documents(directory)
    if not chunks:
        print("未找到可索引的文档")
        return 0

    db = get_db()
    db.add(chunks)
    print(f"完成！共索引 {len(chunks)}个分块")
    return len(chunks)


def search_knowledge(query: str, top_k: int = 5) -> List[Tuple[str, float, dict]]:
    """检索知识"""
    db = get_db()

    # 获取所有文档用于BM25
    all_data = db.collection.get()
    documents = all_data["documents"] if all_data["documents"] else []

    if not documents:
        return []

    # 创建混合检索器并执行
    searcher = HybridSearcher(db, documents)
    results = searcher.search(query, top_k)

    return results


def get_context(query: str, top_k: int = 3) -> str:
    """获取格式化的上下文（直接给LLM）"""
    results = search_knowledge(query, top_k)

    if not results:
        return "未找到相关知识。"

    parts = []
    for doc, score, meta in results:
        source = meta.get("source", "未知")
        parts.append(f"【来源: {source} | 相关度: {score:.2f}】\n{doc}")

    return "\n\n---\n\n".join(parts)