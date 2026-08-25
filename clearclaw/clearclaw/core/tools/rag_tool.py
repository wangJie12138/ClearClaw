# clearclaw/core/tools/rag_tool.py

from langchain_core.tools import tool
from clearclaw.core.rag.retriever import get_context


@tool
def search_knowledge(query: str) -> str:
    """
    从本地知识库中检索信息。
    当用户询问关于公司制度、产品文档、技术规范等内部知识时，你不知道相关的信息的时候，强制使用此工具。
    """
    return get_context(query, top_k=3)

RAG_TOOL = [
    search_knowledge
]