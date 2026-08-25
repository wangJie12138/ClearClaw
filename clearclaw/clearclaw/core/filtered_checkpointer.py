from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata
from langchain_core.messages import ToolMessage, BaseMessage
from typing import Optional, Tuple, Iterable


def filter_rag_tool_messages(messages: list[BaseMessage]) -> list[BaseMessage]:
    """
    持久化前置过滤器
    删除RAG工具search_knowledge产生的ToolMessage
    其余ToolMessage、HumanMessage、AIMessage全部保留
    """
    output = []
    for msg in messages:
        if not isinstance(msg, ToolMessage):
            output.append(msg)
        else:
            # 过滤search_knowledge工具返回消息
            if msg.name != "search_knowledge":
                output.append(msg)
    return output


class AsyncFilteredCheckpointer(BaseCheckpointSaver):
    """异步包装Checkpointer，写入前过滤RAG ToolMessage，兼容新版langgraph所有字段"""
    def __init__(self, origin_saver: BaseCheckpointSaver):
        self.origin_saver = origin_saver

    async def aget(self, config):
        return await self.origin_saver.aget(config)

    async def aget_tuple(self, config) -> Optional[Tuple[Checkpoint, CheckpointMetadata]]:
        return await self.origin_saver.aget_tuple(config)

    async def aput(self, config, checkpoint: Checkpoint, metadata: CheckpointMetadata, new_versions):
        # 拷贝顶层字典，保留全部原生字段
        # 只是修改准备写入数据库的副本，内存里正在运行的graph原始checkpoint对象不会被篡改。
        new_checkpoint = dict(checkpoint)
        channel_values = dict(new_checkpoint["channel_values"])

        if "messages" in channel_values:
            raw_messages = channel_values["messages"]
            channel_values["messages"] = filter_rag_tool_messages(raw_messages)

        new_checkpoint["channel_values"] = channel_values
        return await self.origin_saver.aput(config, new_checkpoint, metadata, new_versions)

    async def aput_writes(self, config, writes: Iterable[tuple[str, object]], task_id: str):
        return await self.origin_saver.aput_writes(config, writes, task_id)

    async def alist(self, config, *, before=None, limit=None):
        return await self.origin_saver.alist(config, before=before, limit=limit)