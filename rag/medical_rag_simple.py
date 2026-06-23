"""
简化版RAG系统 - 用于快速测试和调试
"""
import chromadb
from chromadb.config import Settings

chromadb.config.allow_reset = True

class SimpleMedicalRAG:
    """简化的医疗RAG系统"""

    def __init__(self):
        self.client = chromadb.PersistentClient(path="./rag/chroma_db")
        self.collection = self.client.get_or_create_collection(name="medical_knowledge_base")
        print("[简化RAG] 系统已初始化")

    def simple_retrieve(self, query: str) -> str:
        """简单检索方法"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=1
            )

            if results and results.get('documents'):
                return results['documents'][0][0] if results['documents'][0] else "未找到相关知识"
            return "未找到相关知识"

        except Exception as e:
            return f"检索出错: {str(e)}"

def get_simple_rag() -> SimpleMedicalRAG:
    """获取简化RAG实例"""
    return SimpleMedicalRAG()