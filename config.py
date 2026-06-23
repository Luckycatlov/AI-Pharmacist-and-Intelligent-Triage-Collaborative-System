"""
配置文件 - 支持多模型配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============= 模型配置 =============
# 默认使用千问模型
DEFAULT_MODEL = "qwen"

# 千问模型配置（推荐）
QWEN_BASE_URL = "https://ai.tcmcds.com/v1"
QWEN_API_KEY = "sk-xBRwP0NV2i0fRRTy9a74Cf18196b4077A2Bd048bCe411bB9"
QWEN_MODEL = "myllm"

# 杏林模型配置
XINGLIN_BASE_URL = "https://ai.tcmcds.com/v1"
XINGLIN_API_KEY = "sk-6V4vUePnPQu4fmRJ0232F622807f49E099Ae6e55A23354A7"
XINGLIN_MODEL = "XinLin"

# Anthropic模型配置（备用）
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

# ============= 数据配置 =============
# 数据文件路径
import os
import pathlib

# 获取项目根目录
PROJECT_ROOT = pathlib.Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"

MEDICINE_MANUALS_FILE = str(DATA_DIR / "extracted_manuals.csv")
TCM_CONSENSUS_FILE = str(DATA_DIR / "中医_专家共识_诊疗指南6.17.csv")
PATENT_MEDICINE_FILE = str(DATA_DIR / "中成药V6.17.csv")
INTEGRATED_MEDICINE_FILE = str(DATA_DIR / "中西医V6.17.csv")

# ============= 向量数据库配置 =============
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "medical_knowledge"
TCM_COLLECTION_NAME = "tcm_knowledge"
PATENT_MEDICINE_COLLECTION_NAME = "patent_medicine_knowledge"

# ============= RAG配置 =============
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 3
TOP_K_TCM_RETRIEVAL = 2  # 中医知识检索数量
TOPK_PATIENT_RETRIEVAL = 2  # 中成药检索数量

# ============= 药品数据库配置 =============
# 药品说明书数据
MEDICINE_DB_SIZE = 2056  # 药品说明书数量
MEDICINE_DB_FIELDS = 17  # 药品字段数量

# 中医知识数量
TCM_CONSENSUS_SIZE = 3389
TCM_CONSENSUS_FIELDS = 21

# 中成药数量
PATENT_MEDICINE_SIZE = 644
PATENT_MEDICINE_FIELDS = 18

# 中西医结合知识数量
INTEGRATED_MEDICINE_SIZE = 6225
INTEGRATED_MEDICINE_FIELDS = 19

def get_model_config(model_name: str = None) -> dict:
    """获取模型配置"""
    if model_name is None:
        model_name = DEFAULT_MODEL

    if model_name == "qwen":
        return {
            "base_url": QWEN_BASE_URL,
            "api_key": QWEN_API_KEY,
            "model": QWEN_MODEL,
            "client_type": "openai"
        }
    elif model_name == "xinglin":
        return {
            "base_url": XINGLIN_BASE_URL,
            "api_key": XINGLIN_API_KEY,
            "model": XINGLIN_MODEL,
            "client_type": "openai"
        }
    elif model_name == "anthropic":
        return {
            "api_key": ANTHROPIC_API_KEY,
            "model": ANTHROPIC_MODEL,
            "client_type": "anthropic"
        }
    else:
        # 默认使用千问
        return {
            "base_url": QWEN_BASE_URL,
            "api_key": QWEN_API_KEY,
            "model": QWEN_MODEL,
            "client_type": "openai"
        }
