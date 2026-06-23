"""
智能技能集 - 真正的Skills = 理解 + 数据 + 逻辑

基于用户的核心洞察:
- Skills不是简单的工具调用，而是理解型、推理型、整合型的智能处理
- 真正的智能系统 = LLM理解 + 适当的数据 + 智能路由
- RAG + LLM 已经是一个很好的基础
"""
from data.data_loader import get_data_loader
from utils.llm_client import get_llm_client
from rag.medical_rag import MedicalRAG
import config

class IntelligentSkills:
    """智能技能集 - 提供理解型、推理型、整合型的医疗问答能力"""

    def __init__(self):
        self.data_loader = get_data_loader()
        self.llm_client = get_llm_client(config.DEFAULT_MODEL)
        self.rag = MedicalRAG()

    def comprehensive_medical_analysis(self, user_question: str) -> str:
        """
        综合医疗分析技能 - 真正的Skills

        特点:
        1. 理解型 - LLM理解用户真实意图
        2. 推理型 - 智能分析问题复杂度
        3. 整合型 - 多源信息整合生成答案

        工作流程:
        - 意图理解 -> 信息获取 -> 智能整合 -> 专业回答
        """
        print(f"\n[综合分析] 开始处理: {user_question}")

        # 第一步: 意图理解
        intent_analysis = self._analyze_intent(user_question)
        print(f"  -> 意图分析: {intent_analysis}")

        # 第二步: 信息获取策略选择
        info_strategy = self._select_info_strategy(intent_analysis)
        print(f"  -> 信息策略: {info_strategy}")

        # 第三步: 执行信息获取
        medical_info = self._acquire_medical_info(user_question, info_strategy)

        # 第四步: 智能整合答案
        final_answer = self._integrate_answer(user_question, medical_info, intent_analysis)

        return final_answer

    def _analyze_intent(self, question: str) -> dict:
        """意图理解 - 分析用户的真实意图"""
        # 简化的关键词分析，实际应该使用LLM深度理解
        analysis = {
            "complexity": "simple",
            "category": "general",
            "key_entities": [],
            "requires_precise_data": False
        }

        # 检测关键词
        medicine_keywords = ["药", "服用", "用法", "副作用"]
        disease_keywords = ["病", "症状", "治疗", "分期"]
        complex_keywords = ["比较", "区别", "推荐", "最佳"]

        if any(kw in question for kw in complex_keywords):
            analysis["complexity"] = "complex"
            analysis["requires_precise_data"] = True
        elif any(kw in question for kw in medicine_keywords):
            analysis["category"] = "medicine"
            analysis["requires_precise_data"] = True
        elif any(kw in question for kw in disease_keywords):
            analysis["category"] = "disease"
            analysis["requires_precise_data"] = True

        return analysis

    def _select_info_strategy(self, intent_analysis: dict) -> str:
        """选择信息获取策略"""
        if intent_analysis["complexity"] == "complex":
            return "multi_source_integration"
        elif intent_analysis["requires_precise_data"]:
            return "precise_data_query"
        else:
            return "rag_enhanced"

    def _acquire_medical_info(self, question: str, strategy: str) -> dict:
        """根据策略获取医疗信息"""
        medical_info = {
            "source": "",
            "data": [],
            "confidence": 0.0
        }

        if strategy == "precise_data_query":
            # 精确数据查询
            from data_priority_main_fixed import extract_medicine_name, extract_disease_name

            medicine = extract_medicine_name(question)
            disease = extract_disease_name(question)

            if medicine:
                result = self.data_loader.get_medicine_by_name(medicine)
                if result and result.get("found"):
                    medical_info["source"] = "medicine_database"
                    medical_info["data"] = [result["medicine"]]
                    medical_info["confidence"] = 0.95

            if disease:
                tcm_results = self.data_loader.get_tcm_consensus_by_disease(disease)
                if tcm_results:
                    medical_info["source"] = "tcm_guidance"
                    medical_info["data"] = tcm_results
                    medical_info["confidence"] = 0.90

        elif strategy == "rag_enhanced" or strategy == "multi_source_integration":
            # RAG增强检索
            results = self.rag.retrieve(question, top_k=3)
            if results:
                medical_info["source"] = "rag_knowledge_base"
                medical_info["data"] = results
                medical_info["confidence"] = 0.85

        return medical_info

    def _integrate_answer(self, question: str, medical_info: dict, intent_analysis: dict) -> str:
        """智能整合答案 - 这是真正的Skills体现"""
        if not medical_info["data"]:
            # 没有找到数据，使用通用LLM回答
            return self._general_llm_response(question)

        # 构建上下文
        context = self._build_context(medical_info)

        # 根据意图分析调整system prompt
        system_prompt = self._generate_system_prompt(intent_analysis)

        # LLM智能整合
        response = self.llm_client.messages_create(
            system_prompt=system_prompt,
            user_message=f"用户问题: {question}\n医疗信息:\n{context}",
            max_tokens=1000,
            temperature=0.4
        )

        # 添加数据来源标注
        source_label = self._generate_source_label(medical_info["source"])

        return f"""{response}

---
{source_label}
[提示] 本回答基于专业医疗数据，仅供参考。如有不适请及时就医。"""

    def _build_context(self, medical_info: dict) -> str:
        """构建上下文信息"""
        context_parts = []

        for data in medical_info["data"]:
            if isinstance(data, dict):
                if '药品名称' in data:
                    # 药品信息
                    context_parts.append(f"药品: {data.get('药品名称', '未知')}")
                    context_parts.append(f"成分: {data.get('主要成份', '暂无')}")
                    context_parts.append(f"适应症: {data.get('适应症', '暂无')}")
                elif '文章标题' in data:
                    # 指南信息
                    context_parts.append(f"指南: {data.get('文章标题', '未知')}")
                    context_parts.append(f"治疗原则: {data.get('治疗原则', '暂无')}")

        return "\n".join(context_parts)

    def _generate_system_prompt(self, intent_analysis: dict) -> str:
        """根据意图分析生成system prompt"""
        base_prompt = "你是专业的医疗顾问。基于提供的医疗信息，准确回答用户问题。"

        if intent_analysis["complexity"] == "complex":
            return base_prompt + "请进行综合分析，提供深入的见解。"
        elif intent_analysis["category"] == "medicine":
            return base_prompt + "请重点说明用药指导和注意事项。"
        elif intent_analysis["category"] == "disease":
            return base_prompt + "请重点说明诊疗原则和症状管理。"
        else:
            return base_prompt

    def _generate_source_label(self, source: str) -> str:
        """生成数据来源标注"""
        source_labels = {
            "medicine_database": "数据来源: 真实药品说明书数据库",
            "tcm_guidance": "数据来源: 真实医疗指南数据库",
            "rag_knowledge_base": "数据来源: RAG医疗知识库"
        }
        return source_labels.get(source, "数据来源: 医疗数据系统")

    def _general_llm_response(self, question: str) -> str:
        """通用LLM回答"""
        response = self.llm_client.messages_create(
            system_prompt="你是友好的医疗问答助手。基于你的专业知识回答问题。",
            user_message=question,
            max_tokens=600,
            temperature=0.7
        )

        return f"""{response}

---
[提示] 本回答仅供参考，如有不适请及时就医。"""

def get_intelligent_skills() -> IntelligentSkills:
    """获取智能技能实例"""
    return IntelligentSkills()