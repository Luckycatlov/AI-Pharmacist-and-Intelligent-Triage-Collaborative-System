"""
RAG系统备份文件 - 保留原始实现作为备份
"""
import chromadb
from chromadb.config import Settings
import os

chromadb.config.allow_reset = True

class MedicalRAGBackup:
    """医疗RAG系统 - 备份版本"""

    def __init__(self, collection_name="medical_knowledge_base"):
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path="./rag/chroma_db")
        self.collection = self.client.get_or_create_collection(name=collection_name)
        print(f"[RAG备份] 已加载集合: {collection_name}")

    def retrieve(self, query: str, top_k: int = 3) -> list:
        """检索相关医疗知识"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        return results

    def format_retrieval_context(self, results: list) -> str:
        """格式化检索结果为上下文"""
        if not results or not results.get('documents'):
            return "未找到相关医疗知识。"

        context_parts = []
        for i, (doc, metadata) in enumerate(zip(
            results['documents'][0],
            results.get('metadatas', [{}])[0]
        ), 1):
            source = metadata.get('source', '未知来源')
            context_parts.append(f"[知识{i}] 来源: {source}")
            context_parts.append(doc)
            context_parts.append("")

        return "\n".join(context_parts)