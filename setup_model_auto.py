"""
自动设置模型 - 智能选择最佳下载方式
"""
import os
from sentence_transformers import SentenceTransformer

def auto_setup():
    """自动设置模型 - 智能选择下载方式"""
    model_path = './models/text2vec-base-chinese'

    if os.path.exists(model_path):
        print(f"[自动设置] 模型已存在: {model_path}")
        return True

    print(f"[自动设置] 开始自动设置中文嵌入模型...")

    # 尝试多种下载方式
    success = False

    # 方式1: 直接下载
    try:
        print("[自动设置] 方式1: 直接从HuggingFace下载...")
        model = SentenceTransformer('shibing624/text2vec-base-chinese')
        model.save(model_path)
        success = True
        print("[自动设置] 方式1成功！")

    except Exception as e:
        print(f"[自动设置] 方式1失败: {e}")

        # 方式2: 使用镜像
        try:
            print("[自动设置] 方式2: 使用镜像站点...")
            # 这里可以添加镜像站点的逻辑
            print("[自动设置] 建议手动使用ModelScope下载")
            print("[自动设置] 命令: git clone https://www.modelscope.cn/datasets/AI-ModelScope/text2vec-base-chinese.git")

        except Exception as mirror_error:
            print(f"[自动设置] 方式2失败: {mirror_error}")

    if success:
        print(f"[自动设置] 模型设置成功: {model_path}")
    else:
        print(f"[自动设置] 自动设置失败，请手动下载")

    return success

if __name__ == "__main__":
    auto_setup()