"""
修复编码问题的版本 - 移除所有emoji字符
"""
import sys
import chromadb
from chromadb.config import Settings

chromadb.config.allow_reset = True

def print_header():
    print("=" * 60)
    print("         医药问答系统 (数据优先版)")
    print("    真实医疗数据 + RAG检索 + LLM生成")
    print("=" * 60)

def process_with_data_priority(user_input: str) -> str:
    """
    数据优先策略 - 强制使用加载的医疗数据
    RAG优先策略，简单有效
    """
    print(f"\n[处理问题] {user_input}")

    # 简单分析问题类型
    question_type = analyze_question_type(user_input)
    print(f"  -> 问题类型: {question_type}")

    if question_type == "闲聊":
        return general_chat_response(user_input)
    elif question_type == "药品查询":
        return medicine_query_response(user_input)
    elif question_type == "疾病咨询":
        return disease_consultation_response(user_input)
    else:
        return rag_medical_response(user_input)

def analyze_question_type(text: str) -> str:
    """
    分析问题类型 - 简单关键词匹配，RAG优先
    """
    # 闲聊关键词 - 扩展匹配范围
    chat_keywords = ["你好", "名字", "叫什么", "是谁", "天气", "谢谢", "再见", "是什么"]
    if any(keyword in text for keyword in chat_keywords):
        return "闲聊"

    # 药品关键词
    medicine_keywords = ["药", "服用", "用法", "用量", "副作用", "禁忌"]
    medicine_names = ["布洛芬", "阿司匹林", "对乙酰氨基酚", "小儿清热止咳合剂"]

    if any(keyword in text for keyword in medicine_keywords):
        if any(med in text for med in medicine_names):
            return "药品查询"

    # 疾病关键词
    disease_keywords = ["病", "症状", "治疗", "分期", "诊断"]
    diseases = ["糖尿病", "高血压", "感冒", "头痛", "发热"]

    if any(keyword in text for keyword in disease_keywords):
        if any(disease in text for disease in diseases):
            return "疾病咨询"

    # 默认为RAG医疗咨询
    return "医疗咨询"

def general_chat_response(user_input: str) -> str:
    """通用聊天响应"""
    print("  -> 执行: 通用对话")

    from utils.llm_client import get_llm_client
    import config

    llm_client = get_llm_client(config.DEFAULT_MODEL)

    response = llm_client.messages_create(
        system_prompt="你是医疗问答助手，可以友好地回答一般性问题。",
        user_message=user_input,
        max_tokens=300,
        temperature=0.7
    )

    return f"{response}\n\n如果你有医疗相关问题，我很乐意为你提供专业建议！"

def medicine_query_response(user_input: str) -> str:
    """药品查询响应 - 强制使用真实数据"""
    print("  -> 执行: 真实药品数据查询")

    from utils.llm_client import get_llm_client
    from data.data_loader import get_data_loader
    import config

    llm_client = get_llm_client(config.DEFAULT_MODEL)
    data_loader = get_data_loader()

    # 提取药品名称
    medicine_name = extract_medicine_name(user_input)

    if not medicine_name:
        # 如果没找到药品，尝试用数据查询
        return rag_medical_response(user_input)

    # 查询药品数据
    result = data_loader.get_medicine_by_name(medicine_name)

    if result and result.get("found"):
        medicine_data = result["medicine"]

        # 格式化药品信息
        response = f"""[药品详细信息]
药品名称：{medicine_data.get('药品名称', '未知')}
主要成分：{medicine_data.get('主要成份', '暂无')}
适应症：{medicine_data.get('适应症', '暂无')}
用法用量：{medicine_data.get('用法用量', '暂无')}
禁忌：{medicine_data.get('禁忌', '暂无')}
不良反应：{medicine_data.get('不良反应', '暂无')}
注意事项：{medicine_data.get('注意事项', '暂无')}

数据来源：真实药品说明书数据库"""

        return f"{response}\n\n[提示] 本回答基于真实医疗数据，仅供参考。请遵医嘱使用。"
    else:
        # 数据查询失败，使用RAG
        print(f"  -> 药品'{medicine_name}'未在数据库中找到，使用RAG检索")
        return rag_medical_response(user_input)

def disease_consultation_response(user_input: str) -> str:
    """疾病咨询响应 - 强制使用真实医疗指南数据"""
    print("  -> 执行: 真实医疗指南查询")

    from utils.llm_client import get_llm_client
    from data.data_loader import get_data_loader
    import config

    llm_client = get_llm_client(config.DEFAULT_MODEL)
    data_loader = get_data_loader()

    # 提取疾病名称
    disease_name = extract_disease_name(user_input)

    if disease_name:
        # 查询中医指南
        tcm_results = data_loader.get_tcm_consensus_by_disease(disease_name)

        # 查询中西医指南
        integrated_results = data_loader.get_integrated_medicine_by_disease(disease_name)

        if tcm_results or integrated_results:
            # 使用真实指南数据
            return format_guidance_response(user_input, disease_name, tcm_results, integrated_results, llm_client)
        else:
            print(f"  -> 疾病'{disease_name}'未在指南数据库中找到，使用RAG检索")
            return rag_medical_response(user_input)
    else:
        # 无法提取疾病，使用RAG
        return rag_medical_response(user_input)

def format_guidance_response(user_input: str, disease: str, tcm_results: list, integrated_results: list, llm_client) -> str:
    """格式化指南响应 - 使用真实数据 + LLM整合"""
    response_parts = []

    # 整合中医指南
    if tcm_results:
        response_parts.append("[中医诊疗指导]")
        for i, guidance in enumerate(tcm_results[:3], 1):
            response_parts.append(f"{i}. {guidance.get('文章标题', '未知')}")
            if guidance.get('中医证候'):
                response_parts.append(f"   - 中医证候: {guidance['中医证候']}")
            if guidance.get('治疗原则'):
                response_parts.append(f"   - 治疗原则: {guidance['治疗原则']}")
        response_parts.append("")

    # 整合中西医指南
    if integrated_results:
        response_parts.append("[中西医结合诊疗]")
        for i, guidance in enumerate(integrated_results[:2], 1):
            response_parts.append(f"{i}. {guidance.get('文章标题', '未知')}")
            if guidance.get('中医证候'):
                response_parts.append(f"   - 中医证候: {guidance['中医证候']}")
            if guidance.get('中西医结合治疗'):
                response_parts.append(f"   - 结合治疗: {guidance['中西医结合治疗']}")
        response_parts.append("")

    # 使用LLM整合这些信息回答用户的具体问题
    context = "\n".join(response_parts)

    llm_response = llm_client.messages_create(
        system_prompt="你是专业的医疗顾问。基于提供的真实医疗指南信息，回答用户的具体问题。请提取相关信息，直接、准确地回答。",
        user_message=f"用户问题: {user_input}\n医疗指南信息:\n{context}",
        max_tokens=800,
        temperature=0.3
    )

    return f"""{llm_response}

---
数据来源: 真实医疗指南数据库
[提示] 本回答基于专业医疗指南，仅供参考。请遵医嘱。"""

def rag_medical_response(user_input: str) -> str:
    """RAG医疗响应 - 使用知识库检索"""
    print("  -> 执行: RAG医疗知识库检索")

    try:
        from rag.medical_rag import MedicalRAG
        from utils.llm_client import get_llm_client
        import config

        rag = MedicalRAG()
        results = rag.retrieve(user_input, top_k=3)

        context = rag.format_retrieval_context(results)

        llm_client = get_llm_client(config.DEFAULT_MODEL)

        response = llm_client.messages_create(
            system_prompt="你是专业的医疗助手。基于检索到的医疗知识回答用户问题。",
            user_message=f"用户问题: {user_input}\n\n{context}",
            max_tokens=800,
            temperature=0.5
        )

        return f"""{response}

---
数据来源: RAG医疗知识库
[提示] 本回答仅供参考，如有不适请及时就医。"""

    except Exception as e:
        print(f"  -> RAG检索失败: {e}")
        return f"抱歉，检索医疗知识时出错: {str(e)}。请尝试重新提问。"

def extract_medicine_name(text: str) -> str:
    """提取药品名称"""
    from data.data_loader import get_data_loader
    data_loader = get_data_loader()

    if data_loader.medicine_manuals is not None:
        for medicine in data_loader.medicine_manuals['药品名称']:
            # 确保只处理字符串类型
            if isinstance(medicine, str) and medicine in text:
                return medicine
    return ""

def extract_disease_name(text: str) -> str:
    """提取疾病名称"""
    from data.data_loader import get_data_loader
    data_loader = get_data_loader()

    common_diseases = ["糖尿病", "高血压", "感冒", "头痛", "发热", "咳嗽"]

    if data_loader.tcm_consensus is not None:
        for disease in data_loader.tcm_consensus['病名']:
            # 确保只处理字符串类型
            if isinstance(disease, str) and disease in text:
                return disease

    # 如果数据查询没找到，使用常见疾病列表
    for disease in common_diseases:
        if disease in text:
            return disease

    return ""

def main():
    """主程序"""
    print_header()

    try:
        print("\n[初始化系统]")

        from utils.llm_client import get_llm_client
        from data.data_loader import get_data_loader
        import config

        print("[OK] 模块导入成功")

        # 预加加载数据
        data_loader_obj = get_data_loader()
        print("[OK] 数据加载完成")

        print("\n[系统特色]")
        print("  - 强制使用真实医疗数据（868条记录）")
        print("  - 优先精确数据查询")
        print("  - RAG知识库补充")
        print("  - 友好对话体验")

        print(f"\n[数据基础]")
        print(f"  - 药品说明书: {len(data_loader_obj.medicine_manuals)}条")
        print(f"  - 中医专家共识: {len(data_loader_obj.tcm_consensus)}条")
        print(f"  - 中成药数据: {len(data_loader_obj.patent_medicine)}条")
        print(f"  - 中西医指南: {len(data_loader_obj.integrated_medicine)}条")
        print(f"  - 总计: 868条专业医疗记录")
        print("[OK] 系统初始化完成\n")

        while True:
            try:
                print("=" * 60)
                user_input = input("请输入您的问题（输入 'quit' 退出）: ").strip()

                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("\n[再见] 感谢使用，再见！")
                    break

                if not user_input:
                    print("[警告] 请输入有效的问题\n")
                    continue

                # 处理问题（强制使用数据）
                response = process_with_data_priority(user_input)

                print("=" * 60)
                print("[AI 回答]")
                print("=" * 60)
                print(response)
                print("=" * 60)

            except KeyboardInterrupt:
                print("\n\n[中断] 检测到中断，正在退出...")
                break
            except Exception as e:
                print(f"\n[错误] 处理错误: {str(e)}")

    except Exception as e:
        print(f"\n[错误] 系统初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
