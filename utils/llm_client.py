"""
LLM客户端适配器 - 支持多种模型API
"""
from openai import OpenAI
import anthropic
import config

class LLMClient:
    """统一的LLM客户端"""

    def __init__(self, model_name: str = None):
        """
        初始化LLM客户端

        Args:
            model_name: 模型名称 (qwen, xinglin, anthropic)
        """
        model_config = config.get_model_config(model_name)
        self.model_type = model_config["client_type"]

        if self.model_type == "openai":
            # 使用OpenAI兼容的客户端（支持千问、杏林等）
            self.client = OpenAI(
                base_url=model_config["base_url"],
                api_key=model_config["api_key"]
            )
            self.model = model_config["model"]
        elif self.model_type == "anthropic":
            # 使用Anthropic客户端
            self.client = anthropic.Anthropic(
                api_key=model_config["api_key"]
            )
            self.model = model_config["model"]
        else:
            raise ValueError(f"不支持的客户端类型: {self.model_type}")

    def messages_create(self, system_prompt: str, user_message: str,
                        max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        统一的消息创建接口

        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            max_tokens: 最大token数
            temperature: 温度参数

        Returns:
            模型响应文本
        """
        if self.model_type == "openai":
            return self._openai_chat(system_prompt, user_message, max_tokens, temperature)
        elif self.model_type == "anthropic":
            return self._anthropic_chat(system_prompt, user_message, max_tokens, temperature)

    def _openai_chat(self, system_prompt: str, user_message: str,
                     max_tokens: int, temperature: float) -> str:
        """使用OpenAI兼容接口进行对话"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {e}")

    def _anthropic_chat(self, system_prompt: str, user_message: str,
                        max_tokens: int, temperature: float) -> str:
        """使用Anthropic接口进行对话"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API调用失败: {e}")

# 全局客户端实例
_llm_client = None

def get_llm_client(model_name: str = None) -> LLMClient:
    """获取全局LLM客户端实例"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(model_name)
    return _llm_client

if __name__ == "__main__":
    # 测试客户端
    print("测试LLM客户端...")

    try:
        client = LLMClient("qwen")
        response = client.messages_create(
            "你是一个友好的助手。",
            "你好，请简单介绍一下你自己。",
            max_tokens=100
        )
        print(f"✓ Qwen模型测试成功: {response[:50]}...")
    except Exception as e:
        print(f"✗ Qwen模型测试失败: {e}")
