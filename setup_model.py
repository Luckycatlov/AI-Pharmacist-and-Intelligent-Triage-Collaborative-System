"""
设置中文嵌入模型 - 支持多种下载方式
"""
import os
from sentence_transformers import SentenceTransformer

def setup_model():
    """设置中文嵌入模型"""
    model_path = './models/text2vec-base-chinese'

    # 检查是否已存在
    if os.path.exists(model_path):
        print(f"[设置模型] 模型已存在: {model_path}")
        return model_path

    print(f"[设置模型] 开始设置中文嵌入模型...")

    try:
        # 方式1: 直接从HuggingFace下载
        print("[设置模型] 尝试从HuggingFace下载...")
        model = SentenceTransformer('shibing624/text2vec-base-chinese')
        model.save(model_path)

    except Exception as hf_error:
        print(f"[设置模型] HuggingFace下载失败: {hf_error}")
        print(f"[设置模型] 请使用ModelScope手动下载:")
        print(f"[设置模型] git clone https://www.modelscope.cn/datasets/AI-ModelScope/text2vec-base-chinese.git")

        return None

    print(f"[设置模型] 模型设置完成: {model_path}")
    return model_path

if __name__ == "__main__":
    setup_model()