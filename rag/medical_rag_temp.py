"""
临时RAG系统 - 用于实验新功能
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

chromadb.config.allow_reset = True

class TempMedicalRAG:
    """临时实验性RAG系统"""

    def __init__(self):
        self.client = chromadb.PersistentClient(path="./rag/chroma_db")
        self.collection = self.client.get_or_create_collection(name="medical_knowledge_base")
        print("[临时RAG] 实验性RAG系统已初始化")

    def experimental_retrieve(self, query: str, top_k: int = 5) -> dict:
        """实验性检索方法"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )

            return {
                "success": True,
                "results": results,
                "count": len(results.get('documents', [[]])[0])
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": None
            }

    def test_embedding(self, texts: list) -> list:
        """测试嵌入功能"""
        try:
            model = SentenceTransformer('./models/text2vec-base-chinese')
            embeddings = model.encode(texts)
            print(f"[临时RAG] 成功生成{len(embeddings)}个嵌入向量")
            return embeddings.tolist()

        except Exception as e:
            print(f"[临时RAG] 嵌入生成失败: {e}")
            return []

def get_temp_rag() -> TempMedicalRAG:
    """获取临时RAG实例"""
    return TempMedicalRAG()