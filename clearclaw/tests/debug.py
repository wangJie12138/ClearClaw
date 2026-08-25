from ClearClaw.clearclaw.core.rag.retriever import load_documents

# 复制你电脑真实文件夹路径
chunks = load_documents(r"C:\Users\User\Desktop\project\ClearClaw\ClearClaw\workspace\knowledge")
print("最终 chunks 长度：", len(chunks))