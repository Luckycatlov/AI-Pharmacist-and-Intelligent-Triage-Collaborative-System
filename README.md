# AI Pharmacist and Intelligent Triage Collaborative System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

一个基于真实医疗数据的智能医药问答和导诊协同系统，结合了RAG检索、多智能体路由和LLM生成能力。

## 系统特色

- **数据优先策略**: 强制使用868条真实医疗数据，包括599条药品说明书、92条中医专家共识、45条中成药数据和132条中西医指南
- **智能路由系统**: 多智能体协作，自动分析问题类型并选择最佳处理方式
- **RAG增强检索**: 基于ChromaDB和中文嵌入模型的专业医疗知识检索
- **真正Skills能力**: 理解型、推理型、整合型的智能医疗问答，超越简单工具调用

## 系统架构

```
AI药师和智能导诊协同系统
├── 核心主程序
│   └── data_priority_main_fixed.py - 数据优先策略主程序
├── 智能代理系统 (agents/)
│   ├── router_agent.py - 路由代理，问题分析和处理方式决策
│   └── supervisor_agent.py - 主管代理，系统整体协调
├── 医疗工具集 (tools/)
│   └── medical_tools.py - 专业医疗数据处理工具
├── 智能技能集 (skills/)
│   └── intelligent_skills.py - 理解型、推理型、整合型医疗问答能力
├── RAG系统 (rag/)
│   ├── medical_rag.py - 主要RAG系统
│   ├── medical_rag_backup.py - RAG备份版本
│   ├── medical_rag_simple.py - 简化RAG版本
│   └── medical_rag_temp.py - 实验性RAG版本
├── 数据管理 (data/)
│   └── data_loader.py - 868条医疗数据加载器
├── 工具模块 (utils/)
│   └── llm_client.py - LLM客户端
└── 配置文件
    └── config.py - 系统配置
```

## 数据基础

系统拥有**868条专业医疗记录**：

- **药品说明书**: 599条 - 完整的药品使用信息
- **中医专家共识**: 92条 - 中医诊疗指导原则
- **中成药数据**: 45条 - 中成药详细信息
- **中西医指南**: 132条 - 中西医结合诊疗方案

## 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone https://github.com/Luckycatlov/AI-Pharmacist-and-Intelligent-Triage-Collaborative-System.git
cd AI-Pharmacist-and-Intelligent-Triage-Collaborative-System

# 安装依赖
pip install -r requirements.txt
```

### 2. 模型准备

```bash
# 下载中文嵌入模型
python setup_model.py

# 或使用自动设置
python setup_model_auto.py
```

### 3. 配置API密钥

编辑 `config.py`，配置您的API密钥：

```python
# 选择使用的模型
DEFAULT_MODEL = "qwen"  # 选项: "qwen", "xinglin", "claude"

# 配置相应的API密钥
QWEN_API_KEY = "your_qwen_api_key"
XINGLIN_API_KEY = "your_xinglin_api_key"
CLAUDE_API_KEY = "your_claude_api_key"
```

### 4. 准备医疗数据

将医疗数据CSV文件放入 `data/` 目录：
- `extracted_manuals.csv` - 药品说明书数据
- `中医_专家共识_诊疗指南6.17.csv` - 中医专家共识
- `中成药V6.17.csv` - 中成药数据
- `中西医V6.17.csv` - 中西医指南

### 5. 运行系统

```bash
# 启动数据优先版本
python data_priority_main_fixed.py
```

## 功能特点

### 1. 智能问题分类

系统能够自动识别问题类型：
- **闲聊对话**: 友好的日常交流
- **药品查询**: 精确的药品使用指导
- **疾病咨询**: 专业的疾病诊疗信息
- **医疗咨询**: 全面的医疗知识问答

### 2. 数据优先策略

强制使用真实医疗数据，确保回答的准确性和专业性：

```python
# 药品查询示例
question = "小儿清热止咳合剂的用法用量是什么？"
# 系统会从599条真实药品说明书中查询并给出准确答案

# 疾病咨询示例
question = "糖尿病的分期有哪些呢？"
# 系统会从92条中医专家共识中查找专业诊疗指导
```

### 3. 多智能体协作

- **路由代理**: 智能分析问题，决定最佳处理方式
- **主管代理**: 协调整个系统的运行流程
- **医疗工具**: 提供专业的数据处理能力
- **智能技能**: 实现真正的理解型、推理型问答

### 4. RAG增强检索

基于本地医疗知识库的智能检索，提供更准确的医疗信息。

## 系统要求

- Python 3.8+
- pandas
- chromadb
- sentence-transformers
- openai (用于LLM API调用)

## 依赖安装

```bash
pip install pandas chromadb sentence-transformers openai
```

## 项目特色

### 真正的Skills能力

不同于简单的工具调用，我们的系统实现了：

- **理解型**: LLM深度理解用户意图
- **推理型**: 智能分析问题复杂度
- **整合型**: 多源信息整合生成专业答案

### 数据与AI的完美结合

- **真实数据**: 868条专业医疗记录作为基础
- **智能路由**: 自动选择最佳信息源和处理方式
- **专业回答**: 基于真实数据的准确医疗建议

## 使用示例

```python
# 直接使用主程序
from data_priority_main_fixed import process_with_data_priority

# 药品查询
response = process_with_data_priority("布洛芬的副作用有哪些？")
print(response)

# 疾病咨询
response = process_with_data_priority("高血压的症状有哪些？")
print(response)

# 导诊咨询
response = process_with_data_priority("头痛发热应该挂什么科？")
print(response)
```

## 免责声明

本系统仅供学习和研究使用。系统提供的医疗建议仅供参考，不能替代专业医生的诊断和治疗。

如有医疗需求，请及时就医并咨询专业医生。

## 许可证

MIT License

## 联系方式

GitHub: [Luckycatlov](https://github.com/Luckycatlov)

---

**AI Pharmacist and Intelligent Triage Collaborative System** - 让医疗咨询更智能、更准确、更专业