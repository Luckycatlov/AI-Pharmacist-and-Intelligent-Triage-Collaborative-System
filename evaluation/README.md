# 医疗系统验证与评估层

## 📋 概述

本评估层为医疗问答系统提供了完整的验证与评估功能，确保系统回答的准确性和安全性。

## 🏗️ 架构组成

### 1. **LangSmith评估系统** (`langsmith_evaluator.py`)
- 自动化测试Agent回答准确率
- 构建医疗评估数据集
- 检测药物禁忌、剂量错误等安全问题
- 支持多轮对话记忆测试

### 2. **Guardrails安全护栏** (`guardrails.py`)
- 实时安全检查与风险预警
- 紧急情况识别与干预
- 高危决策人工审核机制
- 药物相互作用检测

### 3. **综合评估框架** (`evaluation_framework.py`)
- 集成LangSmith + Guardrails
- 生成系统健康度报告
- 提供改进建议

## 🚀 快速开始

### 基础评估运行

```bash
# 运行综合评估
python run_evaluation.py
```

### 配置LangSmith（可选）

```bash
# 设置LangChain API Key以启用LangSmith功能
export LANGCHAIN_API_KEY='your-api-key'

# Windows用户
set LANGCHAIN_API_KEY=your-api-key
```

## 📊 评估数据集

评估系统包含以下测试类别：

### 🔒 药物安全性测试
- 禁忌药物检测（孕妇、儿童禁忌）
- 药物相互作用检查
- 过量用药警告

### 👥 特殊人群用药
- 老年人用药安全
- 肝肾功能不全患者
- 儿童用药剂量

### 🎯 准确性测试
- 药品基本信息准确性
- 适应症描述准确性
- 用法用量准确性

### 💬 对话记忆测试
- 代词解析（"这个药" → 具体药品）
- 上下文一致性
- 多轮对话连贯性

### 🚨 Guardrails触发测试
- 紧急情况识别
- 严重副作用处理
- 高危决策预警

## 🛡️ Guardrails安全护栏

### 风险等级
- **安全** (Safe): 无风险，正常通过
- **低危** (Low): 轻微风险，建议注意
- **中危** (Medium): 中度风险，需要警告
- **高危** (High): 高度风险，需要人工审核
- **极高危** (Critical): 极高风险，立即干预

### 护栏措施
- **允许通过** (Allow): 正常执行
- **警告提示** (Warn): 添加安全警告
- **阻止执行** (Block): 阻止危险操作
- **转人工审核** (Escalate): 提交人工审核
- **紧急干预** (Emergency): 立即干预

## 📈 评估指标

### 准确性指标
- 回答正确率
- 关键信息完整性
- 适用场景准确性

### 安全性指标
- 禁忌药物检测率
- 高危情况识别率
- 安全提示完整性

### 系统健康度
- **优秀**: 准确率≥90% + 安全率≥95%
- **良好**: 准确率≥80% + 安全率≥90%
- **一般**: 准确率≥70% + 安全率≥80%
- **需要改进**: 低于一般标准

## 🔧 扩展评估

### 添加自定义测试用例

```python
from evaluation.langsmith_evaluator import LangSmithEvaluator

evaluator = LangSmithEvaluator()

# 创建自定义测试用例
custom_tests = [
    {
        "category": "自定义类别",
        "test_case": "测试名称",
        "question": "测试问题",
        "expected_behavior": "预期行为描述",
        "risk_level": "中危",
        "validation_points": [
            "验证点1",
            "验证点2"
        ]
    }
]

# 运行自定义评估
import pandas as pd
from multi_agents.medical_system import get_multi_agent_system

system = get_multi_agent_system()
results = evaluator.run_evaluation(system, pd.DataFrame(custom_tests))
```

### 添加Guardrails规则

```python
from evaluation.guardrails import MedicalGuardrails

guardrails = MedicalGuardrails()

# 添加自定义高危关键词
guardrails.high_risk_keywords["自定义类别"] = ["关键词1", "关键词2"]

# 添加禁忌药物组合
guardrails.forbidden_combinations.append(("药物A", "药物B"))
```

## 📝 评估报告

评估完成后，系统会生成以下报告：

1. **综合评估报告** (`comprehensive_evaluation_*.json`)
   - 准确性评估结果
   - 安全性评估结果
   - 系统健康度评分
   - 改进建议

2. **Guardrails审核日志** (`guardrails_audit_*.json`)
   - 安全检查详细记录
   - 风险评估历史
   - 护栏触发统计

3. **LangSmith上传** (需要API Key)
   - 自动上传到LangSmith平台
   - 支持在线查看和分析

## ⚠️ 使用建议

1. **定期运行评估**: 建议每次系统更新后运行完整评估
2. **优先处理高危测试失败**: 高危测试失败必须立即修复
3. **持续扩展测试集**: 根据实际使用场景添加测试用例
4. **人工审核重要决策**: 对Guardrails标记的高危案例进行人工审核

## 🔗 集成到主系统

### 在多智能体系统中集成Guardrails

```python
from evaluation.guardrails import MedicalGuardrails

# 初始化Guardrails
guardrails = MedicalGuardrails()

# 在回答前进行安全检查
def safe_response(question, answer):
    # 运行安全检查
    assessment = guardrails.evaluate_response(question, answer)

    # 如果有风险，添加警告
    if not assessment['overall_passed']:
        warning = guardrails.generate_safety_warning(assessment)
        return f"{answer}\n\n{warning}"

    return answer
```

## 📚 相关文件

- `evaluation/langsmith_evaluator.py` - LangSmith评估器
- `evaluation/guardrails.py` - 安全护栏系统
- `evaluation/evaluation_framework.py` - 综合评估框架
- `run_evaluation.py` - 评估运行脚本

## 🤝 贡献

欢迎添加更多测试用例和安全规则来完善评估系统！

## 📞 支持

如有问题或建议，请查看项目文档或联系开发团队。