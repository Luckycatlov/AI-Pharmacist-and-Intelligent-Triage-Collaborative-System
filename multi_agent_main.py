"""
医药问答系统 - 多智能体 + 记忆层版本
基于868条真实医疗数据 + LangGraph多智能体协同
"""
import sys
import os

# 禁用telemetry
os.environ['SENTENCE_TRANSFORMERS_NO_TELEMETRY'] = '1'
os.environ['CHROMA_TELEMETRY'] = 'false'

from multi_agents.medical_system import get_multi_agent_system, create_medical_graph

def print_header():
    print("=" * 60)
    print("    医药问答系统 (多智能体 + 记忆层版本)")
    print("   868条真实数据 + 多智能体协同 + 对话记忆")
    print("=" * 60)

def process_with_multi_agent_memory(user_input: str) -> str:
    """
    使用多智能体系统+记忆层处理用户问题
    """
    print(f"\n[处理问题] {user_input}")

    # 获取多智能体系统
    system = get_multi_agent_system()

    # 如果LangGraph可用，使用图结构
        try:
            workflow = create_medical_graph()
            print(f"[多智能体] 使用LangGraph工作流")

            # 创建初始状态
            from multi_agents.medical_system import MedicalState
            initial_state = MedicalState(
                question=user_input,
                question_type="",
                conversation_history=system.memory_manager.get_conversation_history(),
                analysis_result={},
                rag_result={},
                data_result={},
                final_answer="",
                metadata={}
            )

            # 🆕 修复API调用方式
            try:
                # 方法1: 使用invoke (新版LangGraph)
                final_state = workflow.invoke(initial_state)
            except AttributeError:
                # 方法2: 使用stream (旧版LangGraph)
                print(f"[多智能体] 使用旧版LangGraph API")
                for state_snapshot in workflow.stream(initial_state):
                    final_state = state_snapshot

            result = final_state['final_answer']

            # 添加系统统计信息
            stats = system.get_system_stats()
            result += f"\n\n[系统统计]"
            result += f"\n处理方式: {stats['智能体调用统计']}"
            result += f"\n对话轮数: {stats['对话轮数']}"
            result += f"\n会话ID: {stats['当前会话']}"

            return result

        except Exception as e:
            print(f"[多智能体] LangGraph执行失败: {e}")
            import traceback
            traceback.print_exc()
            print(f"[多智能体] 使用简化的多智能体处理")

        # 降级到简化版本
        result = system.supervisor_agent(user_input)
        answer = result['answer']

        # 添加处理信息
        answer += f"\n\n[处理信息]"
        answer += f"\n问题类型: {result['question_type']}"
        answer += f"\n数据来源: {result['data_source']}"
        answer += f"\n处理路径: {result['processing_agent']}"
        answer += f"\n置信度: {result['confidence']:.2f}"

        return answer

def main():
    """主程序"""
    print_header()

    try:
        print("\n[初始化多智能体医疗系统]")

        from utils.llm_client import get_llm_client
        from data.data_loader import get_data_loader
        from memory.conversation_manager import get_memory_manager
        import config

        print("[OK] 核心组件加载完成")

        # 初始化组件
        llm_client = get_llm_client(config.DEFAULT_MODEL)
        data_loader_obj = get_data_loader()
        memory_manager = get_memory_manager()

        print("[OK] 多智能体系统初始化完成")

        print("\n[系统特色]")
        print("  🤖 多智能体协同 - 路由/聊天/数据/RAG智能体")
        print("  🧠 对话记忆层 - 支持多轮问诊上下文")
        print("  📊 真实医疗数据 - 868条专业医疗记录")
        print("  🔍 RAG知识检索 - 865条真实数据知识库")

        print(f"\n[数据基础]")
        print(f"  药品说明书: {len(data_loader_obj.medicine_manuals)}条")
        print(f"  中医专家共识: {len(data_loader_obj.tcm_consensus)}条")
        print(f"  中成药数据: {len(data_loader_obj.patent_medicine)}条")
        print(f"  中西医指南: {len(data_loader_obj.integrated_medicine)}条")
        print(f"  总计: 868条专业医疗记录")

        print(f"\n[记忆系统]")
        print(f"  当前会话: {memory_manager.current_session_id}")
        print(f"  记忆容量: 10轮对话")

        print("\n[智能体架构]")
        print("  ┌─ 路由智能体 - 问题分析和处理决策")
        print("  ├─ 聊天智能体 - 日常对话处理")
        print("  ├─ 数据智能体 - 868条医疗数据精确查询")
        print("  ├─ RAG智能体 - 865条真实数据知识检索")
        print("  └─ 主管智能体 - 系统协调和响应生成")

        print("[OK] 系统初始化完成\n")

        while True:
            try:
                print("=" * 60)
                user_input = input("请输入您的问题（输入 'quit' 退出，'new' 开始新会话，'stats' 查看统计）: ").strip()

                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("\n[再见] 感谢使用，再见！")
                    # 保存对话记忆
                    memory_manager.save_to_disk()
                    break

                if user_input.lower() in ['new', '新会话']:
                    # 开始新会话
                    new_session = memory_manager.create_session()
                    print(f"[新会话] 已创建新会话: {new_session}")
                    continue

                if user_input.lower() in ['stats', '统计']:
                    # 显示系统统计
                    system = get_multi_agent_system()
                    stats = system.get_system_stats()
                    print("\n[系统统计]")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                    print(f"  会话详情: {memory_manager.get_session_summary()}")
                    continue

                if not user_input:
                    print("[警告] 请输入有效的问题\n")
                    continue

                # 处理问题（多智能体 + 记忆层）
                response = process_with_multi_agent_memory(user_input)

                print("=" * 60)
                print("[AI 回答]")
                print("=" * 60)
                print(response)
                print("=" * 60)

            except KeyboardInterrupt:
                print("\n\n[中断] 检测到中断，正在保存对话记忆...")
                memory_manager.save_to_disk()
                break
            except Exception as e:
                print(f"\n[错误] 处理错误: {str(e)}")
                import traceback
                traceback.print_exc()

    except Exception as e:
        print(f"\n[错误] 系统初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())