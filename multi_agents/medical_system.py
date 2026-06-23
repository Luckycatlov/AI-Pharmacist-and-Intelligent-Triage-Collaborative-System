"""
LangGraph 多智能体医疗系统
基于真实医疗数据的多智能体协同架构
"""
import os
import sys
from typing import Dict, Any, List, TypedDict, Literal
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from langgraph.graph import StateGraph, END
    from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("[警告] LangGraph未安装，将使用简化版本的多智能体系统")

from data.data_loader import get_data_loader
from utils.llm_client import get_llm_client
from rag.medical_rag import MedicalRAG
from memory.conversation_manager import get_memory_manager
import config

# 定义状态类型
class MedicalState(TypedDict):
    """医疗系统状态"""
    question: str
    question_type: str
    conversation_history: List[Dict]
    analysis_result: Dict
    rag_result: Dict
    data_result: Dict
    final_answer: str
    metadata: Dict

class MultiAgentMedicalSystem:
    """多智能体医疗协同系统"""

    def __init__(self):
        """初始化多智能体系统"""
        print("[多智能体] 初始化医疗协同系统...")

        # 核心组件
        self.data_loader = get_data_loader()
        self.llm_client = get_llm_client(config.DEFAULT_MODEL)
        self.rag = MedicalRAG()
        self.memory_manager = get_memory_manager()

        # 创建当前会话
        if self.memory_manager.current_session_id is None:
            self.memory_manager.create_session()

        # 系统统计
        self.stats = {
            "router_agent_calls": 0,
            "data_agent_calls": 0,
            "rag_agent_calls": 0,
            "chat_agent_calls": 0,
            "supervisor_calls": 0
        }

        print("[多智能体] 系统初始化完成")

    def analyze_question_type(self, question: str) -> Dict:
        """
        路由智能体 - 分析问题类型并决定处理策略
        """
        print(f"[路由智能体] 分析问题: {question[:50]}...")
        self.stats["router_agent_calls"] += 1

        # 简化的问题分类逻辑
        chat_keywords = ["你好", "名字", "叫什么", "是谁", "天气", "谢谢", "再见"]
        if any(keyword in question for keyword in chat_keywords):
            return {"question_type": "闲聊", "confidence": 0.9, "reasoning": "检测到闲聊关键词"}

        medicine_keywords = ["药", "服用", "用法", "用量", "副作用", "禁忌"]
        if any(keyword in question for keyword in medicine_keywords):
            return {"question_type": "药品查询", "confidence": 0.8, "reasoning": "检测到药品查询关键词"}

        disease_keywords = ["病", "症状", "治疗", "分期", "诊断"]
        if any(keyword in question for keyword in disease_keywords):
            return {"question_type": "疾病咨询", "confidence": 0.8, "reasoning": "检测到疾病咨询关键词"}

        return {"question_type": "医疗咨询", "confidence": 0.7, "reasoning": "默认使用RAG检索"}

    def chat_agent(self, question: str, conversation_history: List[Dict]) -> str:
        """
        聊天智能体 - 处理日常对话
        """
        print(f"[聊天智能体] 处理日常对话")
        self.stats["chat_agent_calls"] += 1

        response = self.llm_client.messages_create(
            system_prompt="你是友好的医疗问答助手。除了医疗问题，你也可以友好地回答一般性问题。",
            user_message=question,
            max_tokens=300,
            temperature=0.7
        )

        return f"{response}\n\n如果你有医疗相关问题，我很乐意为你提供专业建议！"

    def data_query_agent(self, question: str, question_type: str, conversation_history: List[Dict]) -> Dict:
        """
        数据查询智能体 - 精确查询868条医疗数据
        """
        print(f"[数据智能体] 执行{question_type}数据查询")
        self.stats["data_agent_calls"] += 1

        result = {
            "success": False,
            "data_found": False,
            "records": [],
            "answer": ""
        }

        try:
            if question_type == "药品查询":
                # 从历史中提取药品名称
                entities = self.memory_manager.extract_entities_from_history()
                medicine_name = self._extract_medicine_name(question)

                if medicine_name:
                    data_result = self.data_loader.get_medicine_by_name(medicine_name)
                    if data_result and data_result.get("found"):
                        medicine = data_result["medicine"]
                        result["success"] = True
                        result["data_found"] = True
                        result["records"] = [medicine]
                        result["answer"] = self._format_medicine_info(medicine)
                        result["data_source"] = "599条药品说明书数据库"

            elif question_type == "疾病咨询":
                disease_name = self._extract_disease_name(question)

                if disease_name:
                    # 查询中医专家共识
                    tcm_results = self.data_loader.get_tcm_consensus_by_disease(disease_name)
                    # 查询中西医指南
                    integrated_results = self.data_loader.get_integrated_medicine_by_disease(disease_name)

                    all_results = []
                    if tcm_results:
                        all_results.extend(tcm_results)
                    if integrated_results:
                        all_results.extend(integrated_results)

                    if all_results:
                        result["success"] = True
                        result["data_found"] = True
                        result["records"] = all_results
                        result["answer"] = self._format_disease_info(disease_name, all_results)
                        result["data_source"] = f"{len(tcm_results)}条中医共识 + {len(integrated_results)}条中西医指南"

        except Exception as e:
            result["error"] = str(e)

        return result

    def rag_agent(self, question: str, conversation_history: List[Dict]) -> Dict:
        """
        RAG智能体 - 基于865条真实医疗数据的检索，利用对话历史增强
        """
        print(f"[RAG智能体] 执行知识库检索")
        self.stats["rag_agent_calls"] += 1

        try:
            # 🆕 先从对话历史中提取实体信息
            entities = self.memory_manager.extract_entities_from_history()

            # 🆕 检查是否提到了代词（"这个药"、"那个病"等）
            enhanced_question = self._enhance_question_with_context(question, entities, conversation_history)

            print(f"[RAG智能体] 原问题: {question}")
            print(f"[RAG智能体] 增强问题: {enhanced_question}")

            # 执行RAG检索
            results = self.rag.retrieve(enhanced_question, top_k=3)

            if not results or len(results) == 0:
                return {
                    "success": False,
                    "retrieval_count": 0,
                    "answer": "抱歉，未找到相关的医疗知识。",
                    "entities_extracted": entities
                }

            # 使用LLM整合检索结果，并考虑对话历史
            context = self.rag.format_retrieval_context(results)
            conversation_context = self.memory_manager.format_conversation_context()

            response = self.llm_client.messages_create(
                system_prompt="你是专业的医疗助手。基于检索到的医疗知识和对话历史回答用户问题。如果用户提到'这个药'或'那个病'，请从对话历史中找到具体指的是什么。",
                user_message=f"用户问题: {question}\n\n对话历史:\n{conversation_context}\n\n检索依据:\n{context}",
                max_tokens=800,
                temperature=0.3
            )

            return {
                "success": True,
                "retrieval_count": len(results),
                "results": results,
                "answer": f"""{response}

---
数据来源: RAG医疗知识库 (865条真实医疗记录)
[提示] 本回答仅供参考，如有不适请及时就医。""",
                "data_source": "865条真实医疗数据",
                "entities_extracted": entities
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": f"抱歉，检索医疗知识时出错: {str(e)}。"
            }

    def _enhance_question_with_context(self, question: str, entities: Dict, conversation_history: List[Dict]) -> str:
        """
        利用对话历史增强问题 - 解决"这个药"、"那个病"等代词问题
        """
        # 检测代词
        pronouns_patterns = {
            r"这个药": "药品",
            r"那个药": "药品",
            r"此药": "药品",
            r"该药": "药品",
            r"这种药": "药品",
            r"这个病": "疾病",
            r"那个病": "疾病",
            r"此病": "疾病",
            r"该病": "疾病"
        }

        import re
        enhanced_question = question

        for pattern, entity_type in pronouns_patterns.items():
            if re.search(pattern, question):
                print(f"[RAG智能体] 检测到代词，需要从对话历史中查找具体{entity_type}")

                # 从对话历史中查找最近提到的具体实体
                if entity_type == "药品":
                    medicine = self._find_latest_medicine(conversation_history)
                    if medicine:
                        enhanced_question = question.replace(re.search(pattern, question).group(), medicine)
                        print(f"[RAG智能体] 找到历史药品: {medicine}")

                elif entity_type == "疾病":
                    disease = self._find_latest_disease(conversation_history)
                    if disease:
                        enhanced_question = question.replace(re.search(pattern, question).group(), disease)
                        print(f"[RAG智能体] 找到历史疾病: {disease}")

                break

        return enhanced_question

    def _find_latest_medicine(self, conversation_history: List[Dict]) -> str:
        """从对话历史中查找最近提到的药品"""
        # 搜索最近的用户消息中提到的药品
        for msg in reversed(conversation_history):
            if msg["role"] == "user":
                content = msg["content"]
                # 检查是否包含已知药品名称
                from data.data_loader import get_data_loader
                data_loader = get_data_loader()

                if data_loader.medicine_manuals is not None:
                    for medicine in data_loader.medicine_manuals['药品名称']:
                        if isinstance(medicine, str) and medicine in content:
                            return medicine
        return ""

    def _find_latest_disease(self, conversation_history: List[Dict]) -> str:
        """从对话历史中查找最近提到的疾病"""
        common_diseases = ["糖尿病", "高血压", "感冒", "头痛", "发热", "咳嗽"]

        for msg in reversed(conversation_history):
            if msg["role"] == "user":
                content = msg["content"]
                for disease in common_diseases:
                    if disease in content:
                        return disease
        return ""

    def supervisor_agent(self, question: str) -> Dict:
        """
        主管智能体 - 协调整个系统的运行
        """
        print(f"[主管智能体] 协调处理用户问题")
        self.stats["supervisor_calls"] += 1

        # 1. 路由分析
        analysis = self.analyze_question_type(question)

        # 2. 获取对话历史
        conversation_history = self.memory_manager.get_conversation_history()

        # 3. 根据分析结果调用相应的智能体
        if analysis["question_type"] == "闲聊":
            answer = self.chat_agent(question, conversation_history)
            data_source = "直接LLM回答"

        elif analysis["question_type"] in ["药品查询", "疾病咨询"]:
            data_result = self.data_query_agent(question, analysis["question_type"], conversation_history)

            if data_result.get("success") and data_result.get("data_found"):
                answer = data_result["answer"]
                data_source = data_result.get("data_source", "医疗数据库")
            else:
                # 数据查询无结果，使用RAG
                rag_result = self.rag_agent(question, conversation_history)
                answer = rag_result["answer"]
                data_source = rag_result.get("data_source", "RAG知识库")

        else:  # 医疗咨询
            rag_result = self.rag_agent(question, conversation_history)
            answer = rag_result["answer"]
            data_source = rag_result.get("data_source", "RAG知识库")

        # 4. 保存对话到记忆
        self.memory_manager.add_message("user", question, metadata={"type": analysis["question_type"]})
        self.memory_manager.add_message("assistant", answer, metadata={"source": data_source})

        return {
            "answer": answer,
            "question_type": analysis["question_type"],
            "data_source": data_source,
            "processing_agent": f"主管智能体 → {analysis['question_type']}智能体",
            "confidence": analysis["confidence"]
        }

    def get_system_stats(self) -> Dict:
        """获取系统运行统计"""
        return {
            "智能体调用统计": self.stats,
            "当前会话": self.memory_manager.current_session_id,
            "对话轮数": len([msg for msg in self.memory_manager.get_conversation_history() if msg['role'] == 'user']),
            "会话摘要": self.memory_manager.get_session_summary()
        }

    # 辅助方法
    def _extract_medicine_name(self, text: str) -> str:
        """提取药品名称"""
        if self.data_loader.medicine_manuals is not None:
            for medicine in self.data_loader.medicine_manuals['药品名称']:
                if isinstance(medicine, str) and medicine in text:
                    return medicine
        return ""

    def _extract_disease_name(self, text: str) -> str:
        """提取疾病名称"""
        common_diseases = ["糖尿病", "高血压", "感冒", "头痛", "发热", "咳嗽"]
        if self.data_loader.tcm_consensus is not None:
            for disease in self.data_loader.tcm_consensus['病名']:
                if isinstance(disease, str) and disease in text:
                    return disease
        for disease in common_diseases:
            if disease in text:
                return disease
        return ""

    def _format_medicine_info(self, medicine: Dict) -> str:
        """格式化药品信息"""
        return f"""[药品详细信息]
药品名称：{medicine.get('药品名称', '未知')}
主要成分：{medicine.get('主要成份', '暂无')}
适应症：{medicine.get('适应症', '暂无')}
用法用量：{medicine.get('用法用量', '暂无')}
禁忌：{medicine.get('禁忌', '暂无')}
不良反应：{medicine.get('不良反应', '暂无')}
注意事项：{medicine.get('注意事项', '暂无')}

数据来源：真实药品说明书数据库
[提示] 本回答仅供参考，请遵医嘱使用。"""

    def _format_disease_info(self, disease: str, results: List) -> str:
        """格式化疾病信息"""
        output = [f"[疾病诊疗指导 - {disease}]"]

        for i, guidance in enumerate(results[:3], 1):
            output.append(f"{i}. {guidance.get('文章标题', '未知')}")
            if guidance.get('中医证候'):
                output.append(f"   中医证候: {guidance['中医证候']}")
            if guidance.get('治疗原则'):
                output.append(f"   治疗原则: {guidance['治疗原则']}")

        return "\n".join(output)

# 如果LangGraph可用，创建图结构
if LANGGRAPH_AVAILABLE:
    def create_medical_graph() -> StateGraph:
        """创建LangGraph医疗系统图"""

        # 初始化系统
        system = MultiAgentMedicalSystem()

        def route_question(state: MedicalState) -> MedicalState:
            """路由智能体节点"""
            print(f"[图节点] 路由分析: {state['question']}")
            analysis = system.analyze_question_type(state['question'])
            state['question_type'] = analysis['question_type']
            state['analysis_result'] = analysis
            return state

        def chat_node(state: MedicalState) -> MedicalState:
            """聊天智能体节点"""
            print(f"[图节点] 聊天处理")
            answer = system.chat_agent(state['question'], state.get('conversation_history', []))
            state['final_answer'] = answer
            return state

        def data_query_node(state: MedicalState) -> MedicalState:
            """数据查询智能体节点"""
            print(f"[图节点] 数据查询")
            result = system.data_query_agent(
                state['question'],
                state['question_type'],
                state.get('conversation_history', [])
            )
            state['data_result'] = result

            if result.get('success') and result.get('data_found'):
                state['final_answer'] = result['answer']
            else:
                # 数据查询失败，转向RAG
                state['final_answer'] = "数据查询未找到结果，需要使用RAG检索"

            return state

        def rag_node(state: MedicalState) -> MedicalState:
            """RAG智能体节点"""
            print(f"[图节点] RAG检索")
            result = system.rag_agent(state['question'], state.get('conversation_history', []))
            state['rag_result'] = result
            state['final_answer'] = result['answer']
            return state

        def decide_next_node(state: MedicalState) -> str:
            """决策下一个节点"""
            question_type = state['question_type']

            if question_type == "闲聊":
                return "chat_node"
            elif question_type in ["药品查询", "疾病咨询"]:
                return "data_query_node"
            else:
                return "rag_node"

        def final_response(state: MedicalState) -> MedicalState:
            """最终响应处理"""
            print(f"[图节点] 最终响应")

            # 保存对话记忆
            system.memory_manager.add_message(
                "user",
                state['question'],
                metadata={"type": state['question_type']}
            )

            system.memory_manager.add_message(
                "assistant",
                state['final_answer'],
                metadata={"source": state.get('data_result', {}).get('data_source', "RAG")}
            )

            state['metadata'] = {
                "timestamp": datetime.now().isoformat(),
                "session_id": system.memory_manager.current_session_id
            }

            return state

        # 创建状态图
        workflow = StateGraph(MedicalState)

        # 添加节点
        workflow.add_node("route_question", route_question)
        workflow.add_node("chat_node", chat_node)
        workflow.add_node("data_query_node", data_query_node)
        workflow.add_node("rag_node", rag_node)
        workflow.add_node("final_response", final_response)

        # 设置入口点
        workflow.set_entry_point("route_question")

        # 添加边
        workflow.add_conditional_edges(
            "route_question",
            decide_next_node,
            {
                "chat_node": "chat_node",
                "data_query_node": "data_query_node",
                "rag_node": "rag_node"
            }
        )

        workflow.add_edge("chat_node", "final_response")
        workflow.add_edge("data_query_node", "final_response")
        workflow.add_edge("rag_node", "final_response")
        workflow.add_edge("final_response", END)

        return workflow

def get_multi_agent_system() -> MultiAgentMedicalSystem:
    """获取多智能体系统实例"""
    return MultiAgentMedicalSystem()