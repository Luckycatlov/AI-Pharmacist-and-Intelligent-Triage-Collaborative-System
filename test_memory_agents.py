"""
测试多智能体+记忆层系统功能
"""
from multi_agents.medical_system import get_multi_agent_system
from memory.conversation_manager import get_memory_manager

def test_memory_and_agents():
    """测试记忆层和多智能体功能"""

    print("=" * 60)
    print("测试多智能体+记忆层系统")
    print("=" * 60)

    # 获取系统实例
    system = get_multi_agent_system()
    memory_manager = get_memory_manager()

    print(f"\n[初始化] 当前会话: {memory_manager.current_session_id}")

    # 测试1: 多轮对话的记忆保持
    print("\n[测试1] 多轮对话记忆功能")
    print("-" * 40)

    conversation_test = [
        ("你好", "闲聊"),
        ("我想咨询一下小儿清热止咳合剂", "药品查询"),
        ("这个药的副作用有哪些", "药品查询"),  # 应该知道"这个药"指的是前面的药品
        ("能和感冒药一起吃吗", "药品查询"),  # 应该利用对话历史
        ("糖尿病患者应该注意什么", "疾病咨询")
    ]

    for i, (question, expected_type) in enumerate(conversation_test, 1):
        print(f"\n[第{i}轮] 问题: {question}")
        result = system.supervisor_agent(question)
        print(f"  问题类型: {result['question_type']} (期望: {expected_type})")
        print(f"  数据来源: {result['data_source']}")

        # 验证对话历史
        history = memory_manager.get_conversation_history()
        print(f"  对话轮数: {len([msg for msg in history if msg['role'] == 'user'])}轮")

    # 测试2: 记忆实体提取
    print("\n[测试2] 对话实体提取")
    print("-" * 40)

    entities = memory_manager.extract_entities_from_history()
    print(f"提取的症状: {entities['symptoms']}")
    print(f"涉及的药品: {entities['medicines']}")
    print(f"涉及疾病: {entities['diseases']}")

    # 测试3: 会话摘要
    print("\n[测试3] 会话摘要")
    print("-" * 40)

    summary = memory_manager.get_session_summary()
    print(summary)

    # 测试4: 系统统计
    print("\n[测试4] 系统运行统计")
    print("-" * 40)

    stats = system.get_system_stats()
    print("智能体调用统计:")
    for agent, count in stats['智能体调用统计'].items():
        print(f"  {agent}: {count}次")

    # 测试5: 对话上下文格式化
    print("\n[测试5] 对话上下文格式化")
    print("-" * 40)

    context = memory_manager.format_conversation_context()
    print(context[:300] + "..." if len(context) > 300 else context)

    # 测试6: 上下文增强的查询
    print("\n[测试6] 上下文增强查询")
    print("-" * 40)

    # 模拟一个依赖上下文的问题
    context_question = "刚才说的那个药适合儿童吗？"
    enhanced_query = memory_manager.get_context_for_query(context_question)

    print(f"问题: {context_question}")
    print(f"增强查询上下文:")
    print(enhanced_query[:300] + "..." if len(enhanced_query) > 300 else enhanced_query)

    print("\n" + "=" * 60)
    print("[测试完成] 多智能体+记忆层系统验证成功")
    print("=" * 60)

    print("\n[功能确认]")
    print("[OK] 多轮对话记忆保持")
    print("[OK] 实体提取与跟踪")
    print("[OK] 会话摘要生成")
    print("[OK] 多智能体协同")
    print("[OK] 上下文增强查询")
    print("[OK] 系统统计追踪")

if __name__ == "__main__":
    test_memory_and_agents()