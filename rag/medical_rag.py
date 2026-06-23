"""
RAG医疗知识库系统 - 基于真实868条医疗数据
"""
from typing import List, Dict
import os
import chromadb
from chromadb.config import Settings
import config
import warnings
import logging
import sys
import pandas as pd

# 在导入任何库之前禁用telemetry
os.environ['SENTENCE_TRANSFORMERS_NO_TELEMETRY'] = '1'
os.environ['CHROMA_TELEMETRY'] = 'false'
os.environ['ANONYMIZED_TELEMETRY'] = 'false'

# 禁用chromadb的telemetry
chromadb.config.allow_reset = True

# 禁用所有警告
warnings.filterwarnings('ignore')

# 设置日志级别为ERROR，减少输出
logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
logging.getLogger('chromadb').setLevel(logging.ERROR)

# 禁用标准输出中的telemetry错误
class TelemetrySuppressor:
    """抑制telemetry错误的类"""
    def __init__(self):
        self.original_stderr = sys.stderr
        self.original_stdout = sys.stdout

    def suppress(self):
        """重定向stderr和stdout来过滤telemetry错误"""
        class FilteredOutput:
            def __init__(self, original):
                self.original = original

            def write(self, text):
                if 'telemetry' not in text.lower() and 'Failed to send' not in text:
                    self.original.write(text)

            def flush(self):
                self.original.flush()

        sys.stderr = FilteredOutput(self.original_stderr)
        sys.stdout = FilteredOutput(self.original_stdout)

    def restore(self):
        """恢复原始输出"""
        sys.stderr = self.original_stderr
        sys.stdout = self.original_stdout

class MedicalRAG:
    def __init__(self):
        """初始化RAG系统"""
        # 抑制telemetry错误
        self.suppressor = TelemetrySuppressor()
        self.suppressor.suppress()

        self.embedder = self._load_embedder()
        self.chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
        self.collection = self._get_or_create_collection()
        self._initialize_knowledge_base()

    def _load_embedder(self):
        """加载文本嵌入模型 - 支持多种方式"""
        from sentence_transformers import SentenceTransformer

        # 方案1: 使用本地模型（优先级最高）
        local_model_paths = [
            "./models/text2vec-base-chinese",
            "../models/text2vec-base-chinese",
            "E:/models/text2vec-base-chinese",  # Windows路径
        ]

        for local_path in local_model_paths:
            if os.path.exists(local_path):
                print(f"[OK] 使用本地模型: {local_path}")
                return SentenceTransformer(local_path)

        # 方案2: 使用国内镜像
        print("[INFO] 正在从国内镜像加载模型...")
        try:
            # 使用hf-mirror镜像
            os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
            model = SentenceTransformer('shibing624/text2vec-base-chinese')
            print("[OK] 模型加载成功")
            return model
        except Exception as e:
            print(f"[ERROR] 镜像加载失败: {e}")

        # 方案3: 使用简化模型（更小，下载更快）
        print("[INFO] 尝试使用简化模型...")
        try:
            # 使用paraphrase-multilingual-MiniLM（更小，多语言支持）
            model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("[OK] 简化模型加载成功")
            return model
        except Exception as e:
            print(f"[ERROR] 简化模型加载失败: {e}")

        # 方案4: 最后尝试原始源
        print("[INFO] 尝试原始源...")
        try:
            model = SentenceTransformer('shibing624/text2vec-base-chinese')
            print("[OK] 原始模型加载成功")
            return model
        except Exception as e:
            print(f"[ERROR] 所有模型加载方式都失败了")
            raise Exception(f"无法加载嵌入模型: {e}")

    def _get_or_create_collection(self):
        """获取或创建集合"""
        try:
            return self.chroma_client.get_collection(name=config.COLLECTION_NAME)
        except:
            return self.chroma_client.create_collection(
                name=config.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )

    def _initialize_knowledge_base(self):
        """初始化医疗知识库 - 基于868条真实医疗数据"""
        # 检查是否已有数据
        if self.collection.count() > 0:
            print("[RAG] 知识库已存在，跳过初始化")
            return

        print("[RAG] 开始加载真实医疗数据到知识库...")

        # 延迟导入避免循环依赖
        from data.data_loader import get_data_loader

        data_loader = get_data_loader()
        knowledge_base = []

        # 1. 加载599条药品说明书数据
        print("[RAG] 加载药品说明书数据...")
        if data_loader.medicine_manuals is not None:
            for _, row in data_loader.medicine_manuals.iterrows():
                # 跳过空数据
                if pd.isna(row.get('药品名称', '')):
                    continue

                medicine_text = self._format_medicine_text(row)
                knowledge_base.append({
                    "text": medicine_text,
                    "category": "药品说明书",
                    "source": "药品说明书数据库",
                    "medicine_name": str(row.get('药品名称', ''))
                })

        # 2. 加载92条中医专家共识数据
        print("[RAG] 加载中医专家共识数据...")
        if data_loader.tcm_consensus is not None:
            for _, row in data_loader.tcm_consensus.iterrows():
                if pd.isna(row.get('文章标题', '')):
                    continue

                tcm_text = self._format_tcm_text(row)
                knowledge_base.append({
                    "text": tcm_text,
                    "category": "中医专家共识",
                    "source": "中医专家共识数据库",
                    "disease": str(row.get('病名', ''))
                })

        # 3. 加载45条中成药数据
        print("[RAG] 加载中成药数据...")
        if data_loader.patent_medicine is not None:
            for _, row in data_loader.patent_medicine.iterrows():
                if pd.isna(row.get('药品名称', '')):
                    continue

                patent_text = self._format_patent_medicine_text(row)
                knowledge_base.append({
                    "text": patent_text,
                    "category": "中成药",
                    "source": "中成药数据库",
                    "medicine_name": str(row.get('药品名称', ''))
                })

        # 4. 加载132条中西医指南数据
        print("[RAG] 加载中西医指南数据...")
        if data_loader.integrated_medicine is not None:
            for _, row in data_loader.integrated_medicine.iterrows():
                if pd.isna(row.get('文章标题', '')):
                    continue

                integrated_text = self._format_integrated_medicine_text(row)
                knowledge_base.append({
                    "text": integrated_text,
                    "category": "中西医结合指南",
                    "source": "中西医结合指南数据库",
                    "disease": str(row.get('疾病', ''))
                })

        print(f"[RAG] 数据加载完成，共 {len(knowledge_base)} 条记录")

        # 批量添加到向量数据库（分批处理，避免内存问题）
        batch_size = 100
        for i in range(0, len(knowledge_base), batch_size):
            batch = knowledge_base[i:i+batch_size]
            texts = [item["text"] for item in batch]
            metadatas = [
                {
                    "category": item["category"],
                    "source": item["source"],
                    **({"medicine_name": item["medicine_name"]} if "medicine_name" in item else {}),
                    **({"disease": item["disease"]} if "disease" in item else {})
                }
                for item in batch
            ]
            ids = [f"{item['category']}_{i+j}" for j, item in enumerate(batch)]

            print(f"[RAG] 正在向量化第 {i+1}-{min(i+batch_size, len(knowledge_base))} 条记录...")

            try:
                embeddings = self.embedder.encode(texts).tolist()

                self.collection.add(
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
            except Exception as e:
                print(f"[ERROR] 批次 {i+1}-{min(i+batch_size, len(knowledge_base))} 向量化失败: {e}")

        print(f"[OK] 已初始化RAG知识库，共 {len(knowledge_base)} 条真实医疗记录")

    def _format_medicine_text(self, row) -> str:
        """格式化药品说明书数据为文本"""
        parts = []
        parts.append(f"药品名称：{row.get('药品名称', '')}")
        if not pd.isna(row.get('主要成份', '')):
            parts.append(f"主要成分：{row.get('主要成份', '')}")
        if not pd.isna(row.get('适应症', '')):
            parts.append(f"适应症：{row.get('适应症', '')}")
        if not pd.isna(row.get('用法用量', '')):
            parts.append(f"用法用量：{row.get('用法用量', '')}")
        if not pd.isna(row.get('禁忌', '')):
            parts.append(f"禁忌：{row.get('禁忌', '')}")
        if not pd.isna(row.get('不良反应', '')):
            parts.append(f"不良反应：{row.get('不良反应', '')}")
        if not pd.isna(row.get('注意事项', '')):
            parts.append(f"注意事项：{row.get('注意事项', '')}")
        return "\n".join(parts)

    def _format_tcm_text(self, row) -> str:
        """格式化中医专家共识数据为文本"""
        parts = []
        parts.append(f"疾病：{row.get('病名', '')}")
        if not pd.isna(row.get('文章标题', '')):
            parts.append(f"指导标题：{row.get('文章标题', '')}")
        if not pd.isna(row.get('中医证候', '')):
            parts.append(f"中医证候：{row.get('中医证候', '')}")
        if not pd.isna(row.get('治疗原则', '')):
            parts.append(f"治疗原则：{row.get('治疗原则', '')}")
        if not pd.isna(row.get('辨证论治', '')):
            parts.append(f"辨证论治：{row.get('辨证论治', '')}")
        if not pd.isna(row.get('临床分科', '')):
            parts.append(f"临床分科：{row.get('临床分科', '')}")
        return "\n".join(parts)

    def _format_patent_medicine_text(self, row) -> str:
        """格式化中成药数据为文本"""
        parts = []
        parts.append(f"药品名称：{row.get('药品名称', '')}")
        if not pd.isna(row.get('主要成份', '')):
            parts.append(f"主要成分：{row.get('主要成份', '')}")
        if not pd.isna(row.get('功能主治', '')):
            parts.append(f"功能主治：{row.get('功能主治', '')}")
        if not pd.isna(row.get('用法用量', '')):
            parts.append(f"用法用量：{row.get('用法用量', '')}")
        if not pd.isna(row.get('规格', '')):
            parts.append(f"规格：{row.get('规格', '')}")
        return "\n".join(parts)

    def _format_integrated_medicine_text(self, row) -> str:
        """格式化中西医指南数据为文本"""
        parts = []
        if not pd.isna(row.get('疾病', '')):
            parts.append(f"疾病：{row.get('疾病', '')}")
        if not pd.isna(row.get('文章标题', '')):
            parts.append(f"指导标题：{row.get('文章标题', '')}")
        if not pd.isna(row.get('中医证候', '')):
            parts.append(f"中医证候：{row.get('中医证候', '')}")
        if not pd.isna(row.get('治疗原则', '')):
            parts.append(f"治疗原则：{row.get('治疗原则', '')}")
        if not pd.isna(row.get('中西医结合治疗', '')):
            parts.append(f"中西医结合治疗：{row.get('中西医结合治疗', '')}")
        if not pd.isna(row.get('临床分科', '')):
            parts.append(f"临床分科：{row.get('临床分科', '')}")
        return "\n".join(parts)

    def retrieve(self, query: str, top_k: int = None) -> List[Dict]:
        """
        检索相关医疗知识

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        if top_k is None:
            top_k = config.TOP_K_RETRIEVAL

        # 编码查询
        query_embedding = self.embedder.encode([query]).tolist()

        # 检索
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        # 格式化结果
        retrieved_docs = []
        for i in range(len(results["ids"][0])):
            retrieved_docs.append({
                "text": results["documents"][0][i],
                "category": results["metadatas"][0][i]["category"],
                "distance": results["distances"][0][i]
            })

        return retrieved_docs

    def format_retrieval_context(self, retrieved_docs: List[Dict]) -> str:
        """
        将检索结果格式化为上下文文本

        Args:
            retrieved_docs: 检索结果列表

        Returns:
            格式化的上下文文本
        """
        context = "【相关医疗知识】\n\n"
        for i, doc in enumerate(retrieved_docs, 1):
            context += f"{i}. [{doc['category']}] {doc['text']}\n\n"
        return context