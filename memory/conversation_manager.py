"""
对话历史记忆管理器 - 支持多轮问诊的上下文保持
"""
from typing import List, Dict, Any
from datetime import datetime
import json
import os

class ConversationMemory:
    """对话记忆管理器 - 存储和管理用户的历史对话"""

    def __init__(self, max_history: int = 10, storage_dir: str = "./memory"):
        """
        初始化对话记忆管理器

        Args:
            max_history: 最大保存的对话轮数
            storage_dir: 记忆存储目录
        """
        self.max_history = max_history
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

        # 对话历史存储结构
        self.conversations: Dict[str, List[Dict]] = {}

        # 当前活跃会话
        self.current_session_id = None

    def create_session(self, session_id: str = None) -> str:
        """
        创建新的对话会话

        Args:
            session_id: 会话ID，如果为None则自动生成

        Returns:
            会话ID
        """
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.conversations[session_id] = []
        self.current_session_id = session_id

        print(f"[记忆] 创建新会话: {session_id}")
        return session_id

    def add_message(self, role: str, content: str, session_id: str = None, metadata: Dict = None):
        """
        添加对话消息到历史记录

        Args:
            role: 角色 (user/assistant/system)
            content: 消息内容
            session_id: 会话ID，如果为None使用当前会话
            metadata: 额外的元数据 (问题类型、数据来源等)
        """
        if session_id is None:
            session_id = self.current_session_id

        if session_id is None:
            session_id = self.create_session()

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.conversations[session_id].append(message)

        # 保持历史记录在最大限制内
        if len(self.conversations[session_id]) > self.max_history * 2:  # *2 因为包括user和assistant
            # 移除最旧的对话对
            self.conversations[session_id] = self.conversations[session_id][-(self.max_history * 2):]

        print(f"[记忆] 添加消息到会话 {session_id}: {role} - {content[:30]}...")

    def get_conversation_history(self, session_id: str = None, last_n: int = None) -> List[Dict]:
        """
        获取对话历史记录

        Args:
            session_id: 会话ID，如果为None使用当前会话
            last_n: 获取最近N轮对话，如果为None获取全部

        Returns:
            对话历史列表
        """
        if session_id is None:
            session_id = self.current_session_id

        if session_id is None or session_id not in self.conversations:
            return []

        history = self.conversations[session_id]

        if last_n is not None:
            # 获取最近N轮对话 (每轮包括user和assistant消息)
            return history[-(last_n * 2):]

        return history

    def format_conversation_context(self, session_id: str = None) -> str:
        """
        格式化对话历史为LLM可理解的上下文

        Args:
            session_id: 会话ID

        Returns:
            格式化的对话上下文文本
        """
        history = self.get_conversation_history(session_id)

        if not history:
            return "这是对话的开始。"

        context_parts = ["【对话历史】"]

        for i, msg in enumerate(history):
            role_name = "用户" if msg["role"] == "user" else "AI助手"
            context_parts.append(f"{i+1}. {role_name}: {msg['content']}")

            # 添加元数据信息
            if msg.get("metadata"):
                metadata_info = ", ".join([f"{k}={v}" for k, v in msg["metadata"].items()])
                context_parts.append(f"   (元数据: {metadata_info})")

        return "\n".join(context_parts)

    def get_context_for_query(self, current_question: str, session_id: str = None) -> str:
        """
        为当前问题获取上下文信息

        Args:
            current_question: 当前用户问题
            session_id: 会话ID

        Returns:
            包含历史对话上下文的完整提示
        """
        conversation_context = self.format_conversation_context(session_id)

        context = f"""{conversation_context}

【当前问题】
{current_question}

请结合对话历史和当前问题，提供准确的医疗建议。如果用户提到之前的症状或用药情况，请在回答中考虑这些信息。
"""
        return context

    def extract_entities_from_history(self, session_id: str = None) -> Dict[str, Any]:
        """
        从对话历史中提取关键实体信息

        Args:
            session_id: 会话ID

        Returns:
            提取的实体信息 (症状、药品、疾病等)
        """
        history = self.get_conversation_history(session_id)

        entities = {
            "symptoms": set(),
            "medicines": set(),
            "diseases": set(),
            "questions_asked": []
        }

        # 简单的关键词提取 (可以后续用LLM增强)
        symptom_keywords = ["痛", "热", "咳", "晕", "泻", "乏", "眠"]
        medicine_keywords = ["药", "服用", "注射", "用"]

        for msg in history:
            if msg["role"] == "user":
                content = msg["content"]
                entities["questions_asked"].append(content)

                # 提取症状关键词
                for keyword in symptom_keywords:
                    if keyword in content:
                        entities["symptoms"].add(keyword)

                # 提取药品相关信息
                if any(kw in content for kw in medicine_keywords):
                    entities["medicines"].add(content[:20])  # 简化提取

        return entities

    def save_to_disk(self, session_id: str = None):
        """保存对话记忆到磁盘"""
        if session_id is None:
            session_id = self.current_session_id

        if session_id is None or session_id not in self.conversations:
            return

        filename = os.path.join(self.storage_dir, f"{session_id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversations[session_id], f, ensure_ascii=False, indent=2)

        print(f"[记忆] 会话 {session_id} 已保存到磁盘")

    def load_from_disk(self, session_id: str):
        """从磁盘加载对话记忆"""
        filename = os.path.join(self.storage_dir, f"{session_id}.json")

        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self.conversations[session_id] = json.load(f)
            self.current_session_id = session_id
            print(f"[记忆] 会话 {session_id} 已从磁盘加载")
            return True
        return False

    def get_session_summary(self, session_id: str = None) -> str:
        """
        获取会话摘要信息

        Args:
            session_id: 会话ID

        Returns:
            会话摘要文本
        """
        if session_id is None:
            session_id = self.current_session_id

        if session_id is None or session_id not in self.conversations:
            return "无会话信息"

        history = self.conversations[session_id]
        entities = self.extract_entities_from_history(session_id)

        summary = f"""【会话摘要: {session_id}】
对话轮数: {len([msg for msg in history if msg['role'] == 'user'])} 轮
涉及症状: {', '.join(entities['symptoms']) if entities['symptoms'] else '无'}
涉及药品: {', '.join(entities['medicines']) if entities['medicines'] else '无'}
最后问题: {history[-1]['content'] if history and history[-1]['role'] == 'user' else '无'}
"""
        return summary

# 全局记忆管理器实例
_memory_manager = None

def get_memory_manager() -> ConversationMemory:
    """获取全局记忆管理器实例"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = ConversationMemory()
    return _memory_manager