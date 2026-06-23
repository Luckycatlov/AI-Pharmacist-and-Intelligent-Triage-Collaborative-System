# 医疗问答多智能体协同系统

[![License: MIT](https://imgshots.com/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://imgshots.com/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

一个基于868条真实医疗数据的智能医疗问答系统，结合RAG检索、多智能体协作、对话记忆管理、LangSmith云端监控和Guardrails安全保护的完整企业级解决方案。

## 系统特色

- **真实医疗数据**: 868条专业医疗记录，包括药品说明书、中医专家共识、中成药数据和中西医指南
- **多智能体协作**: 路由、对话、数据查询、RAG检索、主管五大智能体协同工作
- **对话记忆管理**: 智能代词解析，跨轮对话实体提取，上下文一致性维护
- **LangSmith云端监控**: 实时执行追踪，在线数据分析，团队协作共享
- **Guardrails安全保护**: 5级风险评估，7重安全检查，实时护栏措施
- **企业级评估**: 13个综合测试用例，多维度评估标准，详细报告生成

## 系统架构

```
医疗问答多智能体协同系统
├── 核心主程序
│   └── multi_agent_main.py - 多智能体协同主程序
├── 多智能体系统 (multi_agents/)
│   ├── medical_system.py - 医疗协同系统核心
│   └── langgraph_integration.py - LangGraph工作流集成
├── 智能代理系统 (agents/)
│   ├── router_agent.py - 路由代理，问题分析决策
│   └── supervisor_agent.py - 主管代理，系统整体协调
├── 医疗工具集 (tools/)
│   └── medical_tools.py - 专业医疗数据处理工具
├── 智能技能集 (skills/)
│   └── intelligent_skills.py - 理解型、推理型、整合型医疗问答能力
├── RAG系统 (rag/)
│   └── medical_rag.py - 基于ChromaDB的医疗知识检索
├── 对话记忆 (memory/)
│   └── conversation_manager.py - 对话上下文和记忆管理
├── 评估系统 (evaluation/)
│   ├── langsmith_evaluator.py - LangSmith云端评估
│   ├── guardrails.py - 安全护栏系统
│   └── evaluation_framework.py - 综合评估框架
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
# 下载中文嵌入模型（选择一个即可）
python setup_model.py          # 手动设置
python setup_model_auto.py     # 自动设置
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
# 启动多智能体协同系统
python multi_agent_main.py
```

## 运行程序说明

### 🏥 主要运行程序

#### 1. 多智能体主程序 (multi_agent_main.py)

**功能**: 系统主入口，提供完整的多智能体协同问答功能

**特性**:
- 多智能体协同工作（路由、对话、RAG、查询、主管）
- 对话记忆管理和代词解析
- 实时Guardrails安全检查
- 会话统计和日志记录

**运行方式**:
```bash
python multi_agent_main.py
```

**使用场景**: 日常医疗问答，完整功能体验

#### 2. 评估系统 (run_evaluation.py)

**功能**: 运行完整的系统评估，生成详细报告

**特性**:
- 13个综合测试用例
- 准确性和安全性双重评估
- JSON格式详细报告
- 系统健康度评分

**运行方式**:
```bash
python run_evaluation.py
```

**使用场景**: 系统验证，质量检查，性能评估

#### 3. 快速评估 (quick_evaluation.py)

**功能**: 快速验证系统核心功能

**特性**:
- 优化评估标准
- 快速执行测试
- 即时结果反馈

**运行方式**:
```bash
python quick_evaluation.py
```

**使用场景**: 开发调试，快速验证

### ☁️ LangSmith云端监控

#### 4. 启用LangSmith云监控 (enable_langsmith_cloud.py)

**功能**: 启用LangSmith实时云端监控

**特性**:
- 实时执行追踪
- 云端数据存储
- 在线可视化分析
- 团队协作共享

**运行方式**:
```bash
python enable_langsmith_cloud.py
```

**使用场景**: 启用云端监控，在线分析

#### 5. LangSmith设置 (setup_langsmith.py)

**功能**: 配置LangSmith评估系统

**特性**:
- 创建评估数据集
- 配置评估标准
- 优化验证算法

**运行方式**:
```bash
python setup_langsmith.py
```

**使用场景**: LangSmith初始配置，评估定制

#### 6. 检查LangSmith状态 (check_langsmith_status.py)

**功能**: 检查LangSmith集成状态

**特性**:
- API连接验证
- 配置检查
- 功能测试

**运行方式**:
```bash
python check_langsmith_status.py
```

**使用场景**: 故障排查，状态验证

### 🔧 模型设置

#### 7. 模型下载设置 (setup_model.py / setup_model_auto.py)

**功能**: 下载和配置中文嵌入模型

**特性**:
- 自动下载text2vec-base-chinese模型
- ChromaDB向量数据库初始化
- 知识库构建

**运行方式**:
```bash
python setup_model.py          # 手动设置
python setup_model_auto.py     # 自动设置
```

**使用场景**: 首次安装，模型更新

## 功能特点

### 1. 智能问题分类

系统能够自动识别问题类型：
- **闲聊对话**: 友好的日常交流
- **药品查询**: 精确的药品使用指导
- **疾病咨询**: 专业的疾病诊疗信息
- **医疗咨询**: 全面的医疗知识问答

### 2. 多智能体协作

**路由智能体**: 分析问题，决定处理方式
- 闲聊识别：直接对话处理
- 药品查询：调用数据查询工具
- 疾病咨询：RAG知识检索
- 综合咨询：多信息源整合

**对话智能体**: 自然对话交互
- 友好的对话界面
- 上下文理解
- 情感化回应

**数据查询智能体**: 精确数据检索
- 药品信息查询
- 用法用量检索
- 禁忌症检查

**RAG智能体**: 知识库检索
- 语义相似度搜索
- 多文档信息整合
- 专业医疗知识提取

**主管智能体**: 系统协调
- 智能路由分发
- 结果整合优化
- 质量控制检查

### 3. 对话记忆管理

**代词解析**: 
- "这个药" → 具体药品名称
- "那种症状" → 上下文中的具体症状
- "它" → 正确的实体引用

**上下文记忆**:
- 跨轮对话实体保持
- 对话历史分析
- 语义一致性维护

### 4. Guardrails安全保护

**5级风险评估**:
- 安全 (Safe): 无风险，正常通过
- 低危 (Low): 轻微风险，建议注意
- 中危 (Medium): 中度风险，需要警告
- 高危 (High): 高度风险，需要人工审核
- 极高危 (Critical): 极高风险，立即干预

**7重安全检查**:
- 紧急情况识别（呼吸困难、胸痛等）
- 禁忌药物检测（孕妇、儿童禁忌）
- 药物相互作用检查
- 年龄安全验证
- 剂量安全检查
- 推荐药物安全性
- 特殊人群保护

**5种护栏措施**:
- 允许通过 (Allow)
- 警告提示 (Warn)
- 阻止执行 (Block)
- 转人工审核 (Escalate)
- 紧急干预 (Emergency)

### 5. LangSmith云端监控

**实时追踪**: 所有Agent执行自动记录
**云端存储**: 评估结果自动上传
**在线分析**: LangSmith平台可视化
**团队协作**: 多用户共享项目
**历史追踪**: 评估趋势分析

## 评估系统

### 评估数据集

**13个综合测试用例**，涵盖6大类别：

#### 🔒 药物安全性测试 (3个)
- 禁忌药物检测（孕妇、儿童禁忌）
- 药物相互作用检查
- 过量用药警告

#### 👥 特殊人群用药 (2个)
- 老年人用药安全
- 肝肾功能不全患者

#### 🎯 准确性测试 (2个)
- 药品基本信息准确性
- 适应症描述准确性

#### 💬 对话记忆测试 (2个)
- 代词解析（"这个药" → 具体药品）
- 上下文一致性

#### 🚨 Guardrails触发测试 (2个)
- 紧急情况识别
- 严重副作用处理

#### 🔄 边界情况测试 (2个)
- 复杂多药物问题
- 跨领域综合咨询

### 评估指标

**准确性指标**:
- 回答正确率: 100% (13/13)
- 关键信息完整性: 优秀
- 适用场景准确性: 完美

**安全性指标**:
- 禁忌药物检测率: 100% (9/9)
- 高危情况识别率: 100%
- 安全提示完整性: 优秀

**系统健康度**: 
- **优秀** ⭐⭐⭐⭐⭐
- 准确率: 100%
- 安全率: 100%

## 使用示例

### 基础问答

```bash
# 启动系统
python multi_agent_main.py

# 示例问答
用户: 小儿清热止咳合剂的主要成分是什么？
系统: 小儿清热止咳合剂的主要成分包括麻黄、石膏、甘草、苦杏仁、金银花等...

用户: 2岁孩子发烧可以用阿司匹林吗？
系统: 不建议2岁儿童使用阿司匹林，因为存在瑞氏综合征风险...
[安全警告]: 儿童使用阿司匹林有极高风险，建议使用对乙酰氨基酚等替代药物
```

### 对话记忆测试

```bash
用户: 小儿清热止咳合剂的主要成分是什么？
系统: [详细回答药品成分]

用户: 这个药的副作用有哪些？
系统: 小儿清热止咳合剂的副作用包括...[正确解析"这个药"为"小儿清热止咳合剂"]

用户: 那种症状可以服用吗？
系统: 根据上下文，针对发热、咳嗽等症状可以服用...
[正确从对话历史中提取症状信息]
```

### LangSmith云监控

```bash
# 1. 启用云监控
python enable_langsmith_cloud.py

# 2. 运行问答系统（自动记录）
python multi_agent_main.py

# 3. 访问LangSmith平台
# https://smith.langchain.com/o/9c8e16fb-d6a-429e-918e-9b115badef92

# 4. 查看实时traces、执行轨迹、评估结果
```

### 系统评估

```bash
# 完整评估
python run_evaluation.py

# 快速评估
python quick_evaluation.py

# 查看评估报告
# evaluation/results/comprehensive_evaluation_*.json
```

## 系统要求

- Python 3.8+
- pandas
- chromadb
- sentence-transformers
- langsmith
- langchain-core
- openai (用于LLM API调用)

## 依赖安装

```bash
pip install pandas chromadb sentence-transformers langsmith langchain-core openai
```

## 系统架构亮点

### 真正的Skills能力

不同于简单的工具调用，我们的系统实现了：

**理解型**: LLM深度理解用户意图和上下文
**推理型**: 智能分析问题复杂度和最佳处理方式  
**整合型**: 多源信息整合生成专业准确答案

### 数据与AI的完美结合

- **真实数据**: 868条专业医疗记录作为基础
- **智能路由**: 自动选择最佳信息源和处理方式
- **专业回答**: 基于真实数据的准确医疗建议
- **安全保护**: 实时风险检查和护栏措施

### 企业级特性

- **云端监控**: LangSmith实时追踪和在线分析
- **安全保护**: Guardrails七重安全检查
- **质量保证**: 完整的评估体系和测试框架
- **对话记忆**: 智能上下文管理和代词解析

## 项目成就

### 评估成果

- ✅ **100%评估通过率** (13/13测试用例)
- ✅ **100%安全检查率** (9/9安全测试)
- ✅ **完整的多智能体协作**
- ✅ **实时Guardrails安全保护**
- ✅ **LangSmith云端监控集成**

### 技术突破

- ✅ **智能代词解析**: "这个药"正确解析为具体药品
- ✅ **对话记忆管理**: 跨轮对话实体提取和保持
- ✅ **多智能体协调**: LangGraph工作流集成
- ✅ **安全护栏系统**: 5级风险7重检查
- ✅ **云端评估分析**: LangSmith实时监控

## 免责声明

本系统仅供学习和研究使用。系统提供的医疗建议仅供参考，不能替代专业医生的诊断和治疗。

如有医疗需求，请及时就医并咨询专业医生。

## 许可证

MIT License

## 联系方式

GitHub: [Luckycatlov](https://github.com/Luckycatlov)

---

**医疗问答多智能体协同系统** - 让医疗咨询更智能、更准确、更专业、更安全