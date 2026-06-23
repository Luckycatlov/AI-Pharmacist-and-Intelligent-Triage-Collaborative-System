"""
医疗系统安全护栏 (Guardrails) - 确保高危决策有兜底
"""
import re
import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from enum import Enum

class RiskLevel(Enum):
    """风险等级"""
    SAFE = "安全"
    LOW = "低危"
    MEDIUM = "中危"
    HIGH = "高危"
    CRITICAL = "极高危"

class GuardrailAction(Enum):
    """护栏措施"""
    ALLOW = "允许通过"
    WARN = "警告提示"
    BLOCK = "阻止执行"
    ESCALATE = "转人工审核"
    EMERGENCY = "紧急干预"

class MedicalGuardrails:
    """医疗系统安全护栏"""

    def __init__(self):
        """初始化安全护栏"""
        print("[护栏] 医疗安全护栏系统启动")

        # 加载安全规则
        self.high_risk_keywords = self._load_high_risk_keywords()
        self.forbidden_combinations = self._load_drug_combinations()
        self.age_restrictions = self._load_age_restrictions()
        self.emergency_keywords = self._load_emergency_keywords()

        # 审核记录
        self.audit_log = []

    def evaluate_response(self, question: str, answer: str, context: Dict = None) -> Dict[str, Any]:
        """
        评估问答是否安全

        Args:
            question: 用户问题
            answer: 系统回答
            context: 对话上下文

        Returns:
            评估结果，包含风险等级和建议措施
        """
        context = context or {}

        # 多重安全检查
        checks = {
            "emergency_check": self._check_emergency_indicators(question, answer),
            "high_risk_check": self._check_high_risk_keywords(question, answer),
            "contraindication_check": self._check_contraindications(question, answer, context),
            "age_safety_check": self._check_age_safety(question, answer, context),
            "dosage_check": self._check_dosage_safety(question, answer),
            "recommendation_check": self._check_recommendation_safety(question, answer)
        }

        # 综合风险评估
        risk_assessment = self._assess_overall_risk(checks)

        # 记录审核结果
        audit_record = {
            "timestamp": datetime.now().isoformat(),
            "question": question[:200],
            "answer_summary": answer[:200],
            "checks": checks,
            "risk_assessment": risk_assessment,
            "context": context
        }
        self.audit_log.append(audit_record)

        return risk_assessment

    def _check_emergency_indicators(self, question: str, answer: str) -> Dict[str, Any]:
        """检查紧急情况指标"""
        emergency_indicators = []

        # 检查问题中的紧急指标
        for keyword in self.emergency_keywords:
            if keyword in question:
                emergency_indicators.append({
                    "keyword": keyword,
                    "location": "question",
                    "severity": "critical"
                })

        # 检查回答是否正确处理了紧急情况
        if emergency_indicators:
            if not any(word in answer for word in ["立即", "马上", "紧急", "就医", "医院", "急救"]):
                return {
                    "passed": False,
                    "risk_level": RiskLevel.CRITICAL,
                    "action": GuardrailAction.EMERGENCY,
                    "reason": "检测到紧急情况但回答未建议立即就医",
                    "indicators": emergency_indicators
                }

        return {
            "passed": True,
            "risk_level": RiskLevel.SAFE,
            "action": GuardrailAction.ALLOW,
            "indicators": emergency_indicators
        }

    def _check_high_risk_keywords(self, question: str, answer: str) -> Dict[str, Any]:
        """检查高危关键词"""
        detected_risks = []

        for category, keywords in self.high_risk_keywords.items():
            for keyword in keywords:
                if keyword in question:
                    detected_risks.append({
                        "category": category,
                        "keyword": keyword,
                        "in_question": True
                    })
                if keyword in answer:
                    detected_risks.append({
                        "category": category,
                        "keyword": keyword,
                        "in_answer": True
                    })

        if not detected_risks:
            return {
                "passed": True,
                "risk_level": RiskLevel.SAFE,
                "action": GuardrailAction.ALLOW
            }

        # 🆕 检查回答中是否已经包含了正确的安全提示
        safety_keywords = ["不能", "禁止", "不建议", "风险", "危险", "注意", "咨询医生", "遵医嘱"]
        has_safety_warning = any(keyword in answer for keyword in safety_keywords)

        # 根据检测到的风险和回答内容确定措施
        risk_categories = set([r['category'] for r in detected_risks])

        if "怀孕" in risk_categories or "儿童禁忌" in risk_categories:
            # 如果回答已经包含了正确的安全提示，则通过
            if has_safety_warning:
                return {
                    "passed": True,
                    "risk_level": RiskLevel.LOW,
                    "action": GuardrailAction.ALLOW,
                    "reason": f"检测到特殊人群，但回答已包含安全提示",
                    "detected_risks": detected_risks
                }
            else:
                return {
                    "passed": False,
                    "risk_level": RiskLevel.HIGH,
                    "action": GuardrailAction.WARN,
                    "reason": f"检测到特殊人群用药，需要加强安全提示",
                    "detected_risks": detected_risks
                }

        return {
            "passed": True,
            "risk_level": RiskLevel.LOW,
            "action": GuardrailAction.ALLOW,
            "reason": f"检测到风险关键词，但回答适当",
            "detected_risks": detected_risks
        }

    def _check_contraindications(self, question: str, answer: str, context: Dict) -> Dict[str, Any]:
        """检查药物禁忌和相互作用"""
        # 提取问题中提到的药物
        mentioned_drugs = self._extract_drug_names(question)

        if len(mentioned_drugs) < 2:
            return {
                "passed": True,
                "risk_level": RiskLevel.SAFE,
                "action": GuardrailAction.ALLOW
            }

        # 检查药物组合
        for drug_pair in self.forbidden_combinations:
            if all(drug in mentioned_drugs for drug in drug_pair):
                # 检查回答中是否警告了风险
                if not any(word in answer for word in ["禁忌", "不能", "禁止", "避免", "风险"]):
                    return {
                        "passed": False,
                        "risk_level": RiskLevel.CRITICAL,
                        "action": GuardrailAction.BLOCK,
                        "reason": f"检测到禁忌药物组合: {' + '.join(drug_pair)}",
                        "contraindicated_pair": drug_pair
                    }

        return {
            "passed": True,
            "risk_level": RiskLevel.SAFE,
            "action": GuardrailAction.ALLOW,
            "checked_drugs": mentioned_drugs
        }

    def _check_age_safety(self, question: str, answer: str, context: Dict) -> Dict[str, Any]:
        """检查年龄相关的安全性"""
        # 提取年龄信息
        age_info = self._extract_age_info(question)

        if not age_info:
            return {
                "passed": True,
                "risk_level": RiskLevel.SAFE,
                "action": GuardrailAction.ALLOW
            }

        age = age_info['age']
        age_unit = age_info['unit']

        # 转换为岁
        if age_unit == "岁" and age < 3:
            # 3岁以下儿童
            if "小儿" not in answer and "儿童" not in answer:
                return {
                    "passed": False,
                    "risk_level": RiskLevel.HIGH,
                    "action": GuardrailAction.WARN,
                    "reason": f"检测到{age}岁幼儿，但回答未充分强调儿童用药安全"
                }

        elif age_unit == "岁" and age > 65:
            # 65岁以上老年人
            if "老年" not in answer and "老人" not in answer and "剂量" not in answer:
                return {
                    "passed": False,
                    "risk_level": RiskLevel.MEDIUM,
                    "action": GuardrailAction.WARN,
                    "reason": f"检测到{age}岁老年人，但回答未提及剂量调整"
                }

        return {
            "passed": True,
            "risk_level": RiskLevel.SAFE,
            "action": GuardrailAction.ALLOW,
            "age_info": age_info
        }

    def _check_dosage_safety(self, question: str, answer: str) -> Dict[str, Any]:
        """检查剂量安全性"""
        # 检查是否询问过量
        overdose_indicators = ["加倍", "多服", "过量", "超量", "多吃"]
        if any(indicator in question for indicator in overdose_indicators):
            if not any(warning in answer for warning in ["不可", "不能", "禁止", "危险", "毒性"]):
                return {
                    "passed": False,
                    "risk_level": RiskLevel.HIGH,
                    "action": GuardrailAction.BLOCK,
                    "reason": "用户询问过量用药，但回答未充分警告风险"
                }

        # 检查回答中的剂量建议
        dosage_pattern = r"(\d+\.?\d*)\s*(毫克|g|ml|片|粒|次)"
        dosages = re.findall(dosage_pattern, answer)

        # 简单的合理性检查
        for dosage, unit in dosages:
            amount = float(dosage)
            if unit == "片" and amount > 5:
                return {
                    "passed": False,
                    "risk_level": RiskLevel.MEDIUM,
                    "action": GuardrailAction.WARN,
                    "reason": f"建议剂量较高: {dosage}{unit}"
                }

        return {
            "passed": True,
            "risk_level": RiskLevel.SAFE,
            "action": GuardrailAction.ALLOW
        }

    def _check_recommendation_safety(self, question: str, answer: str) -> Dict[str, Any]:
        """检查推荐药物的安全性"""
        # 检查是否推荐了药物
        drug_recommendation_pattern = r"(推荐|建议|可以服用|可以使用)"
        recommends_drug = bool(re.search(drug_recommendation_pattern, answer))

        if recommends_drug:
            # 检查是否有适当的安全提示
            safety_mentions = [
                "咨询医生", "遵医嘱", "副作用", "禁忌", "注意事项",
                "请在医生指导下", "建议咨询"
            ]

            has_safety_mention = any(mention in answer for mention in safety_mentions)

            if not has_safety_mention:
                return {
                    "passed": False,
                    "risk_level": RiskLevel.MEDIUM,
                    "action": GuardrailAction.WARN,
                    "reason": "推荐了药物但未提供充分的安全提示"
                }

        return {
            "passed": True,
            "risk_level": RiskLevel.SAFE,
            "action": GuardrailAction.ALLOW
        }

    def _assess_overall_risk(self, checks: Dict[str, Dict]) -> Dict[str, Any]:
        """综合评估整体风险"""
        failed_checks = [name for name, result in checks.items() if not result.get('passed', True)]

        if not failed_checks:
            return {
                "overall_passed": True,
                "overall_risk": RiskLevel.SAFE,
                "overall_action": GuardrailAction.ALLOW,
                "message": "所有安全检查通过",
                "checks": checks
            }

        # 找出最高风险等级
        risk_levels = [checks[name]['risk_level'] for name in failed_checks]
        max_risk = max(risk_levels, key=lambda x: {
            RiskLevel.SAFE: 0, RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4
        }.get(x, 0))

        # 确定最终措施
        if max_risk == RiskLevel.CRITICAL:
            final_action = GuardrailAction.ESCALATE
            message = "检测到极高危风险，需要人工审核"
        elif max_risk == RiskLevel.HIGH:
            final_action = GuardrailAction.WARN
            message = "检测到高危风险，已添加警告"
        else:
            final_action = GuardrailAction.WARN
            message = "检测到中等风险，建议谨慎"

        return {
            "overall_passed": False if max_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL] else True,
            "overall_risk": max_risk,
            "overall_action": final_action,
            "message": message,
            "failed_checks": failed_checks,
            "checks": checks
        }

    def _extract_drug_names(self, text: str) -> List[str]:
        """从文本中提取药物名称"""
        # 简化版：只检查常见的药物名称
        common_drugs = [
            "阿司匹林", "华法林", "布洛芬", "对乙酰氨基酚", "肝素",
            "地高辛", "地西泮", "美托洛尔", "卡马西平", "苯妥英钠"
        ]

        found_drugs = [drug for drug in common_drugs if drug in text]
        return found_drugs

    def _extract_age_info(self, text: str) -> Optional[Dict]:
        """从文本中提取年龄信息"""
        age_patterns = [
            r"(\d+)\s*岁",
            r"(\d+)\s*个月",
            r"(\d+)\s*月大",
            r"(\d+)\s*周"
        ]

        for pattern in age_patterns:
            match = re.search(pattern, text)
            if match:
                age = int(match.group(1))
                unit = "岁" if "岁" in pattern else (
                    "月" if "月" in pattern else "周"
                )
                return {"age": age, "unit": unit}

        return None

    def _load_high_risk_keywords(self) -> Dict[str, List[str]]:
        """加载高危关键词"""
        return {
            "怀孕": ["怀孕", "孕期", "妊娠", "孕妇", "胎儿"],
            "儿童禁忌": ["阿司匹林", "儿童", "瑞氏综合征"],
            "肝肾功能": ["肝功能", "肾功能", "肾衰竭", "肝衰竭"],
            "心血管": ["心脏病", "高血压", "心衰", "心律失常"],
            "过敏": ["过敏", "过敏性", "休克", "荨麻疹"]
        }

    def _load_drug_combinations(self) -> List[Tuple[str, str]]:
        """加载禁忌药物组合"""
        return [
            ("阿司匹林", "华法林"),  # 出血风险
            ("阿司匹林", "肝素"),    # 出血风险
            ("地高辛", "维拉帕米"),  # 心动过缓
            ("卡马西平", "红霉素"),  # 毒性增加
            ("苯妥英钠", "华法林"),  # 相互作用
        ]

    def _load_age_restrictions(self) -> Dict[str, Dict]:
        """加载年龄限制"""
        return {
            "阿司匹林": {"min_age": 16, "reason": "瑞氏综合征风险"},
            "对乙酰氨基酚": {"min_age": 0, "max_age": 3, "reason": "幼儿剂量需调整"},
        }

    def _load_emergency_keywords(self) -> List[str]:
        """加载紧急情况关键词"""
        return [
            "呼吸困难", "窒息", "喘不过气",
            "胸痛", "心悸", "心跳剧烈",
            "昏迷", "意识不清", "晕厥",
            "大出血", "严重出血",
            "过敏反应", "过敏性休克",
            "中毒", "过量", "自杀",
            "癫痫发作", "抽搐",
            "高烧", "持续高烧", "体温过高",
            "脱水", "严重脱水"
        ]

    def generate_safety_warning(self, assessment: Dict[str, Any]) -> str:
        """根据风险评估生成安全警告"""
        if assessment['overall_passed']:
            return ""

        warnings = []
        action = assessment['overall_action']

        if action == GuardrailAction.EMERGENCY:
            warnings.append("[紧急] 请立即就医！")
        elif action == GuardrailAction.ESCALATE:
            warnings.append("[高危] 此建议需要专业医生确认")
        elif action == GuardrailAction.BLOCK:
            warnings.append("[禁止] 此用药方案存在安全风险")
        elif action == GuardrailAction.WARN:
            warnings.append("[注意] 请仔细阅读安全提示")

        warnings.append(assessment['message'])

        return "\n".join(warnings)

    def save_audit_log(self, filename: str = None):
        """保存审核日志"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"guardrails_audit_{timestamp}.json"

        filepath = f"./evaluation/results/{filename}"
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.audit_log, f, ensure_ascii=False, indent=2)

        print(f"[护栏] 审核日志已保存: {filepath}")
        return filepath


def get_medical_guardrails() -> MedicalGuardrails:
    """获取全局护栏实例"""
    return MedicalGuardrails()