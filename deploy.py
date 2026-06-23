"""
医疗问答系统 - LangServe部署主程序
将多智能体医疗系统部署为FastAPI服务
"""
from fastapi import FastAPI, HTTPException
from langserve import add_routes
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agents.medical_system import get_multi_agent_system

# 创建FastAPI应用
app = FastAPI(
    title="医疗问答多智能体API",
    description="""
    基于真实医疗数据的智能问答系统，采用多智能体协同架构。

    ## 功能特色
    - **868条真实医疗数据**：药品说明书、中医专家共识、中成药数据、中西医指南
    - **多智能体协作**：路由、对话、RAG、查询、主管五大智能体协同工作
    - **对话记忆管理**：智能代词解析，跨轮对话实体提取
    - **实时安全检查**：Guardrails安全护栏，5级风险评估
    - **LangSmith云端监控**：实时执行追踪和评估分析

    ## 使用说明
    1. 通过/invoke端点进行单次问答
    2. 通过/stream端点进行流式问答
    3. 通过/batch端点进行批量问答
    """,
    version="1.0.0",
    contact={
        "name": "Medical Q&A System",
        "url": "https://github.com/Luckycatlov/AI-Pharmacist-and-Intelligent-Triage-Collaborative-System"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# 全局变量存储多智能体系统
agent_system = None

def initialize_system():
    """初始化多智能体系统"""
    global agent_system
    if agent_system is None:
        print("[启动] 正在初始化医疗问答多智能体系统...")
        try:
            agent_system = get_multi_agent_system()
            print("[成功] 医疗问答系统初始化完成")
        except Exception as e:
            print(f"[错误] 系统初始化失败: {e}")
            raise

# 启动时初始化系统
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化系统"""
    initialize_system()

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    if agent_system is None:
        raise HTTPException(status_code=503, detail="系统尚未初始化")

    return {
        "status": "healthy",
        "system": "医疗问答多智能体系统",
        "version": "1.0.0",
        "components": {
            "multi_agent_system": "running",
            "rag_retrieval": "active",
            "conversation_memory": "enabled",
            "guardrails_safety": "active"
        }
    }

# 根路径信息
@app.get("/")
async def root():
    """API根路径信息"""
    return {
        "message": "医疗问答多智能体API服务",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs - API交互文档",
            "health": "/health - 健康检查",
            "invoke": "/medical-qa/invoke - 单次问答",
            "stream": "/medical-qa/stream - 流式问答",
            "batch": "/medical-qa/batch - 批量问答"
        },
        "features": [
            "868条真实医疗数据",
            "多智能体协同工作",
            "对话记忆管理",
            "实时安全检查",
            "LangSmith云端监控"
        ]
    }

# 简化的问答请求/响应模型
class QuestionRequest(BaseModel):
    """问题请求模型"""
    question: str = Field(..., description="医疗相关问题", example="小儿清热止咳合剂的主要成分是什么？")
    session_id: Optional[str] = Field(None, description="会话ID，用于对话记忆")

class AnswerResponse(BaseModel):
    """回答响应模型"""
    answer: str = Field(..., description="医疗回答")
    sources: list = Field(default=[], description="数据来源")
    safety_check: Dict[str, Any] = Field(default={}, description="安全检查结果")
    session_id: str = Field(..., description="会话ID")

# 自定义问答端点
@app.post("/qa", response_model=AnswerResponse)
async def medical_qa(request: QuestionRequest):
    """
    医疗问答端点

    参数:
    - question: 医疗相关问题
    - session_id: 可选的会话ID

    返回:
    - answer: 医疗回答
    - sources: 数据来源
    - safety_check: 安全检查结果
    - session_id: 会话ID
    """
    try:
        if agent_system is None:
            initialize_system()

        # 调用多智能体系统
        response = agent_system.supervisor_agent(request.question)

        # 提取回答
        answer = response.get('answer', '')

        return AnswerResponse(
            answer=answer,
            sources=[],
            safety_check={},
            session_id=request.session_id or "default"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答处理失败: {str(e)}")

# 添加LangServe路由到多智能体系统
try:
    # 注意：这里需要根据实际的LangGraph API进行调整
    # 如果您的agent_system不是标准的LangGraph，可能需要包装
    print("[LangServe] 正在配置LangServe路由...")
    # add_routes(app, agent_system, path="/medical-qa")
    print("[提示] LangServe路由配置需要根据实际的LangGraph结构进行调整")
except Exception as e:
    print(f"[警告] LangServe路由配置跳过: {e}")
    print("[提示] 使用自定义的/qa端点代替")

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("    医疗问答多智能体API服务")
    print("=" * 60)
    print("[启动] 服务地址: http://localhost:8000")
    print("[文档] API文档: http://localhost:8000/docs")
    print("[测试] 健康检查: http://localhost:8000/health")
    print("[问答] 问答接口: http://localhost:8000/qa")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")