"""
运行医疗系统评估
"""
import os
import sys
from evaluation.evaluation_framework import MedicalSystemEvaluator

def main():
    """主函数"""
    print("启动医疗系统评估")
    print("=" * 60)

    # 获取LangChain API Key（可选）
    langchain_api_key = os.getenv("LANGCHAIN_API_KEY")

    if not langchain_api_key:
        print("\n[提示] LangSmith集成:")
        print("  - 当前使用本地评估模式")
        print("  - 要启用LangSmith功能，请设置:")
        print("    export LANGCHAIN_API_KEY='your-api-key'")
        print("  - 或在代码中传入API Key")
        print()

    # 创建评估器
    evaluator = MedicalSystemEvaluator(langchain_api_key)

    # 运行评估
    try:
        report = evaluator.run_comprehensive_evaluation()

        print("\n" + "=" * 60)
        print("[评估完成]")
        print("=" * 60)

        # 显示关键结果
        health = report['系统健康度']
        print(f"系统健康度: {health['overall']}")
        print(f"   准确性: {health['accuracy']} ({health['accuracy_score']*100:.1f}%)")
        print(f"   安全性: {health['safety']} ({health['safety_score']*100:.1f}%)")

        print(f"\n改进建议 ({len(report['改进建议'])}项):")
        for i, suggestion in enumerate(report['改进建议'], 1):
            print(f"   {i}. {suggestion}")

        print("\n评估结果已保存到 ./evaluation/results/")

        return 0

    except Exception as e:
        print(f"\n[❌ 评估失败] {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())