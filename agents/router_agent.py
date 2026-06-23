"""
路由代理 - 分析用户问题并决定最佳处理方式
"""
from utils.llm_client import get_llm_client
import config

class RouterAgent:
    """路由代理 - 决定如何处理用户问题"""

    def __init__(self):
        self.llm_client = get_llm_client(config.DEFAULT_MODEL)

    def analyze_question(self, user_input: str) -> dict:
        """
        分析问题并决定处理方式

        返回格式:
        {
            "question_type": "闲聊|药品查询|疾病咨询|医疗咨询",
            "processing_method": "direct_llm|rag|data_query|complex",
            "confidence": 0.8,
            "reasoning": "选择原因"
        }
        """
        # 简化的关键词分析
        chat_keywords = ["你好", "名字", "天气", "谢谢", "再见"]
        medicine_keywords = ["药", "服用", "用法", "用量", "副作用", "禁忌"]
        disease_keywords = ["病", "症状", "治疗", "分期", "诊断"]

        if any(keyword in user_input for keyword in chat_keywords):
            return {
                "question_type": "闲聊",
                "processing_method": "direct_llm",
                "confidence": 0.9,
                "reasoning": "检测到闲聊关键词"
            }

        if any(keyword in user_input for keyword in medicine_keywords):
            return {
                "question_type": "药品查询",
                "processing_method": "data_query",
                "confidence": 0.8,
                "reasoning": "检测到药品查询关键词"
            }

        if any(keyword in user_input for keyword in disease_keywords):
            return {
                "question_type": "疾病咨询",
                "processing_method": "data_query",
                "confidence": 0.8,
                "reasoning": "检测到疾病咨询关键词"
            }

        # 默认使用RAG
        return {
            "question_type": "医疗咨询",
            "processing_method": "rag",
            "confidence": 0.7,
            "reasoning": "使用RAG进行医疗知识检索"
        }

def get_router_agent() -> RouterAgent:
    """获取路由代理实例"""
    return RouterAgent()