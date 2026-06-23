"""
RAG医疗知识库系统 - 支持离线/国内镜像
"""
from typing import List, Dict
import os
import chromadb
from chromadb.config import Settings
import config
import warnings
import logging
import sys

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
        """初始化医疗知识库"""
        # 检查是否已有数据
        if self.collection.count() > 0:
            return

        # 医疗知识库（模拟数据）
        knowledge_base = [
            {
                "text": "头痛是一种常见的症状，可能由紧张、偏头痛、高血压、颈椎病等引起。对于轻微头痛，可休息、多喝水；如持续严重应就医检查明确病因。",
                "category": "症状知识",
                "keywords": ["头痛", "头疼", "头部疼痛"]
            },
            {
                "text": "发热是身体对感染或炎症的反应。体温超过37.3℃为低热，超过38.5℃为中高热。低热可物理降温（温水擦浴），高热需使用退热药（如对乙酰氨基酚）并就医。",
                "category": "症状知识",
                "keywords": ["发热", "发烧", "体温高"]
            },
            {
                "text": "咳嗽是呼吸道疾病的常见症状。急性咳嗽多由感冒引起，一般1-2周自愈。如咳嗽持续超过3周或伴有胸痛、咳血，应立即就医进行胸部CT等检查。",
                "category": "症状知识",
                "keywords": ["咳嗽", "干咳", "咳痰"]
            },
            {
                "text": "腹痛病因复杂，可能涉及消化系统、泌尿系统、妇科等。如腹痛剧烈、持续超过6小时、伴有呕吐或便血，应立即急诊就医，勿自行服药。",
                "category": "症状知识",
                "keywords": ["腹痛", "肚子痛", "胃痛"]
            },
            {
                "text": "胸痛可能是心脏病、肺部疾病或肌肉骨骼问题引起。如出现胸痛伴呼吸困难、冷汗、恶心，可能是心肌梗死，需立即拨打120急救。不要自行驾车就医。",
                "category": "急症知识",
                "keywords": ["胸痛", "胸口痛", "胸闷"]
            },
            {
                "text": "高血压患者应定期监测血压，坚持服药。如血压持续高于140/90mmHg，需调整药物。建议低盐饮食、适量运动、控制体重。避免突然停药。",
                "category": "慢病管理",
                "keywords": ["高血压", "血压高"]
            },
            {
                "text": "糖尿病患者需定期监测血糖，按时用药或注射胰岛素。出现低血糖（心慌、出汗）时应立即补充糖分。定期检查眼底、肾功能，预防并发症。",
                "category": "慢病管理",
                "keywords": ["糖尿病", "血糖"]
            },
            {
                "text": "导诊建议：头痛患者可先就诊神经内科。如伴有视力异常，可同时考虑眼科；如有外伤史，就诊神经外科。突发剧烈头痛需急诊排除脑血管意外。",
                "category": "导诊建议",
                "keywords": ["头痛", "导诊", "科室"]
            },
            {
                "text": "导诊建议：发热患者可先就诊发热门诊或内科。如伴有咳嗽、呼吸困难，就诊呼吸内科；如伴有腹泻、腹痛，就诊消化内科；高热不退建议急诊。",
                "category": "导诊建议",
                "keywords": ["发热", "发烧", "导诊"]
            },
            {
                "text": "导诊建议：腹痛患者根据部位就诊。上腹痛多考虑消化内科；下腹痛右侧考虑阑尾炎（普外科），左侧考虑妇科（女性）；尿痛伴发热考虑泌尿外科。",
                "category": "导诊建议",
                "keywords": ["腹痛", "肚子痛", "导诊"]
            },
            {
                "text": "导诊建议：咳嗽患者主要就诊呼吸内科。如咳嗽超过3周或伴有痰中带血，需做胸部CT。儿童咳嗽就诊儿科，孕妇咳嗽就诊产科高危门诊。",
                "category": "导诊建议",
                "keywords": ["咳嗽", "导诊", "科室"]
            },
            {
                "text": "用药安全：不可同时服用多种含相同成分的感冒药，可能造成药物过量损伤肝肾。服药期间禁止饮酒，可能加重不良反应或产生毒性。",
                "category": "用药安全",
                "keywords": ["用药", "安全", "药物"]
            },
            {
                "text": "儿童用药需特别谨慎，严格按体重计算剂量，不可使用成人药。阿司匹林儿童禁用（可能引起瑞氏综合征）。建议使用儿童专用剂型。",
                "category": "用药安全",
                "keywords": ["儿童", "用药", "安全"]
            },
            {
                "text": "老年人用药应遵循'小剂量开始，缓慢递增'原则。肝肾功能减退者需调整剂量。注意药物相互作用，建议将所有用药清单带给医生审核。",
                "category": "用药安全",
                "keywords": ["老人", "老年人", "用药"]
            },
            {
                "text": "孕妇用药应谨慎。妊娠早期（前3个月）尽量避免用药，必须用药时选择B类药物。禁止使用四环素、喹诺酮类、ACEI/ARB类药物。就诊时告知怀孕情况。",
                "category": "用药安全",
                "keywords": ["孕妇", "妊娠", "用药"]
            }
        ]

        # 添加知识到向量数据库
        texts = [item["text"] for item in knowledge_base]
        metadatas = [
            {
                "category": item["category"],
                "keywords": ",".join(item["keywords"])
            }
            for item in knowledge_base
        ]
        ids = [f"doc_{i}" for i in range(len(knowledge_base))]

        embeddings = self.embedder.encode(texts).tolist()

        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

        print(f"[OK] 已初始化医疗知识库，共 {len(knowledge_base)} 条记录")

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