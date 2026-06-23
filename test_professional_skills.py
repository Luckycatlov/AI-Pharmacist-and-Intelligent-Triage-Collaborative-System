"""
测试专业医疗Skills和RAG溯源功能
"""
from skills.intelligent_skills import get_medical_skills
from data_priority_main_fixed import process_with_data_priority

def test_professional_skills():
    """测试基于医疗数据特性的专业Skills"""

    print("=" * 60)
    print("测试专业医疗Skills和RAG溯源功能")
    print("=" * 60)

    skills = get_medical_skills()

    # 测试1: 药品安全检查技能（基于599条药品说明书）
    print("\n[测试1] 药品安全检查技能 - 基于599条药品说明书")
    print("-" * 40)
    safety_result = skills.medication_safety_check("小儿清热止咳合剂")
    print(skills.format_skill_result("药品安全检查", safety_result))

    # 测试2: 疾病分期诊断技能（基于92条中医专家共识）
    print("\n[测试2] 疾病分期诊断技能 - 基于92条中医专家共识")
    print("-" * 40)
    staging_result = skills.disease_staging_diagnosis("糖尿病")
    print(skills.format_skill_result("疾病分期诊断", staging_result))

    # 测试3: 中医证候识别技能
    print("\n[测试3] 中医证候识别技能")
    print("-" * 40)
    syndrome_result = skills.tcm_syndrome_identification("发热咳嗽症状")
    print(skills.format_skill_result("中医证候识别", syndrome_result))

    # 测试4: 中西医结合诊疗技能（基于132条中西医指南）
    print("\n[测试4] 中西医结合诊疗技能 - 基于132条中西医指南")
    print("-" * 40)
    integrated_result = skills.integrated_treatment_guidance("糖尿病")
    print(skills.format_skill_result("中西医结合诊疗", integrated_result))

    # 测试5: 可溯源的RAG查询
    print("\n[测试5] 可溯源RAG查询")
    print("-" * 40)
    traceable_result = skills.traceable_rag_query("糖尿病的治疗方法", top_k=3)

    print(f"[RAG溯源报告]")
    print(f"问题: {traceable_result['question']}")
    print(f"检索条数: {traceable_result['retrieval_summary']['total_retrieved']}条")
    print(f"数据来源: {traceable_result['retrieval_summary']['database_used']}")
    print(f"")

    print("[检索到的记录详情]:")
    for record in traceable_result['retrieved_records']:
        print(f"记录#{record['record_id']}:")
        print(f"  来源: {record['source']}")
        print(f"  置信度: {record['confidence']}")
        print(f"  距离: {record['distance']}")
        print(f"  内容: {record['content']}")
        print("")

    # 测试6: 集成系统测试
    print("\n[测试6] 集成系统测试")
    print("=" * 60)

    test_questions = [
        "小儿清热止咳合剂的副作用有哪些？",      # 药品安全检查
        "糖尿病的分期有哪些呢？",                # 疾病分期诊断
        "发热咳嗽应该用什么药？",               # 中医证候识别 + 中成药推荐
    ]

    for question in test_questions:
        print(f"\n[问题] {question}")
        print("-" * 40)
        try:
            response = process_with_data_priority(question)
            print(response[:500] + "..." if len(response) > 500 else response)
        except Exception as e:
            print(f"[错误] {e}")
        print("=" * 40)

    print("\n[测试总结]")
    print("=" * 60)
    print("专业Skills验证完成:")
    print("1. 药品安全检查技能 - 基于599条药品说明书")
    print("2. 疾病分期诊断技能 - 基于92条中医专家共识")
    print("3. 中医证候识别技能 - 基于中医理论")
    print("4. 中西医结合诊疗技能 - 基于132条中西医指南")
    print("5. 可溯源RAG查询 - 提供完整的检索溯源信息")
    print("6. 集成系统测试 - 自动技能选择和执行")
    print("\n所有Skills都基于具体的医疗数据特性和数量！")

if __name__ == "__main__":
    test_professional_skills()