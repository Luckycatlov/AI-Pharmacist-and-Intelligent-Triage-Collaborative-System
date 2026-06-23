"""
主管代理 - 协调整个医疗问答系统的运行
"""
from agents.router_agent import get_router_agent
from data.data_loader import get_data_loader
from utils.llm_client import get_llm_client
import config

class SupervisorAgent:
    """主管代理 - 协调各个组件"""

    def __init__(self):
        self.router_agent = get_router_agent()
        self.data_loader = get_data_loader()
        self.llm_client = get_llm_client(config.DEFAULT_MODEL)

    def process_question(self, user_input: str) -> str:
        """
        处理用户问题

        工作流程:
        1. 路由分析 - 决定问题类型和处理方式
        2. 数据处理 - 根据路由结果选择处理方式
        3. 答案生成 - 生成最终回复
        """
        print(f"\n[主管代理] 处理问题: {user_input}")

        # 1. 路由分析
        routing_decision = self.router_agent.analyze_question(user_input)
        print(f"  -> 路由决策: {routing_decision}")

        # 2. 根据路由结果处理
        if routing_decision["processing_method"] == "direct_llm":
            return self._direct_llm_response(user_input)
        elif routing_decision["processing_method"] == "data_query":
            return self._data_query_response(user_input)
        elif routing_decision["processing_method"] == "rag":
            return self._rag_response(user_input)
        else:
            return self._rag_response(user_input)  # 默认使用RAG

    def _direct_llm_response(self, user_input: str) -> str:
        """直接LLM回答"""
        print("  -> 执行: 直接LLM回答")

        response = self.llm_client.messages_create(
            system_prompt="你是医疗问答助手，可以友好地回答一般性问题。",
            user_message=user_input,
            max_tokens=300,
            temperature=0.7
        )

        return f"{response}\n\n如果你有医疗相关问题，我很乐意为你提供专业建议！"

    def _data_query_response(self, user_input: str) -> str:
        """数据查询回答"""
        print("  -> 执行: 数据查询")

        # 提取关键信息并查询数据
        from data_priority_main_fixed import extract_medicine_name, extract_disease_name

        medicine_name = extract_medicine_name(user_input)
        disease = extract_disease_name(user_input)

        if medicine_name:
            result = self.data_loader.get_medicine_by_name(medicine_name)
            if result and result.get("found"):
                return self._format_medicine_response(result["medicine"])

        if disease:
            tcm_results = self.data_loader.get_tcm_consensus_by_disease(disease)
            if tcm_results:
                return self._format_disease_response(disease, tcm_results)

        # 如果数据查询无结果，使用RAG
        return self._rag_response(user_input)

    def _rag_response(self, user_input: str) -> str:
        """RAG检索回答"""
        print("  -> 执行: RAG检索")

        try:
            from rag.medical_rag import MedicalRAG

            rag = MedicalRAG()
            results = rag.retrieve(user_input, top_k=3)
            context = rag.format_retrieval_context(results)

            response = self.llm_client.messages_create(
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

    def _format_medicine_response(self, medicine: dict) -> str:
        """格式化药品响应"""
        return f"""[药品详细信息]
药品名称：{medicine.get('药品名称', '未知')}
主要成分：{medicine.get('主要成份', '暂无')}
适应症：{medicine.get('适应症', '暂无')}
用法用量：{medicine.get('用法用量', '暂无')}
禁忌：{medicine.get('禁忌', '暂无')}
不良反应：{medicine.get('不良反应', '暂无')}
注意事项：{medicine.get('注意事项', '暂无')}

数据来源：真实药品说明书数据库"""

    def _format_disease_response(self, disease: str, results: list) -> str:
        """格式化疾病响应"""
        guidance = results[0]  # 取第一条结果
        return f"""[疾病诊疗指导]
疾病：{disease}
指导标题：{guidance.get('文章标题', '暂无')}
临床科室：{guidance.get('临床分科', '暂无')}
治疗原则：{guidance.get('治疗原则', '暂无')}
中医证候：{guidance.get('中医证候', '暂无')}
治疗方法：{guidance.get('辨证论治', '暂无')}

数据来源: 真实医疗指南数据库
[提示] 本回答基于专业医疗指南，仅供参考。请遵医嘱。"""

def get_supervisor_agent() -> SupervisorAgent:
    """获取主管代理实例"""
    return SupervisorAgent()