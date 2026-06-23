"""
医疗工具集 - 提供专业的医疗数据处理工具
"""
from data.data_loader import get_data_loader
from utils.llm_client import get_llm_client
import config

class MedicalTools:
    """医疗工具集 - 封装专业医疗数据处理功能"""

    def __init__(self):
        self.data_loader = get_data_loader()
        self.llm_client = get_llm_client(config.DEFAULT_MODEL)

    def query_medicine_by_name(self, medicine_name: str) -> dict:
        """
        根据药品名称查询详细信息

        参数:
            medicine_name: 药品名称

        返回:
            {
                "found": True/False,
                "medicine": {...药品信息}
            }
        """
        result = self.data_loader.get_medicine_by_name(medicine_name)
        return result

    def query_tcm_guidance(self, disease: str) -> list:
        """
        查询中医专家共识指南

        参数:
            disease: 疾病名称

        返回:
            [指南1, 指南2, ...]
        """
        results = self.data_loader.get_tcm_consensus_by_disease(disease)
        return results

    def query_integrated_medicine(self, disease: str) -> list:
        """
        查询中西医结合诊疗指南

        参数:
            disease: 疾病名称

        返回:
            [指南1, 指南2, ...]
        """
        results = self.data_loader.get_integrated_medicine_by_disease(disease)
        return results

    def format_medicine_info(self, medicine_data: dict) -> str:
        """
        格式化药品信息为可读文本

        参数:
            medicine_data: 药品数据字典

        返回:
            格式化的药品信息文本
        """
        return f"""[药品详细信息]
药品名称：{medicine_data.get('药品名称', '未知')}
主要成分：{medicine_data.get('主要成份', '暂无')}
适应症：{medicine_data.get('适应症', '暂无')}
用法用量：{medicine_data.get('用法用量', '暂无')}
禁忌：{medicine_data.get('禁忌', '暂无')}
不良反应：{medicine_data.get('不良反应', '暂无')}
注意事项：{medicine_data.get('注意事项', '暂无')}"""

    def format_guidance_info(self, guidance_data: dict, disease: str = "") -> str:
        """
        格式化指南信息为可读文本

        参数:
            guidance_data: 指南数据字典
            disease: 疾病名称（可选）

        返回:
            格式化的指南信息文本
        """
        disease_prefix = f"（{disease}）" if disease else ""
        return f"""[疾病诊疗指导{disease_prefix}]
指导标题：{guidance_data.get('文章标题', '暂无')}
临床科室：{guidance_data.get('临床分科', '暂无')}
治疗原则：{guidance_data.get('治疗原则', '暂无')}
中医证候：{guidance_data.get('中医证候', '暂无')}
治疗方法：{guidance_data.get('辨证论治', '暂无')}"""

    def intelligent_summary(self, user_question: str, medical_data: list) -> str:
        """
        智能汇总 - 使用LLM整合医疗数据回答用户问题

        参数:
            user_question: 用户问题
            medical_data: 医疗数据列表

        返回:
            针对性的回答
        """
        context = "\n".join([
            self.format_medicine_info(data) if '药品名称' in data
            else self.format_guidance_info(data)
            for data in medical_data
        ])

        response = self.llm_client.messages_create(
            system_prompt="你是专业的医疗顾问。基于提供的医疗数据，准确回答用户问题。",
            user_message=f"用户问题: {user_question}\n医疗数据:\n{context}",
            max_tokens=800,
            temperature=0.3
        )

        return response

def get_medical_tools() -> MedicalTools:
    """获取医疗工具实例"""
    return MedicalTools()