import os

from dotenv import load_dotenv

from .base import BaseLLMClient
from .ollama_client import OllamaClient
from .api_client import DeepSeekClient, OpenAIClient

load_dotenv()


class LLMFactory:
    """根据配置自动创建对应的 LLM 客户端"""
    
    _providers = {
        "ollama": OllamaClient,
        "deepseek": DeepSeekClient,
        "openai": OpenAIClient,
    }
    
    @classmethod
    def create(cls, provider: str = None, **kwargs) -> BaseLLMClient:
        provider = (provider or os.getenv("LLM_PROVIDER", "ollama")).lower().strip()
        
        if provider not in cls._providers:
            raise ValueError(
                f"不支持的 LLM 提供商: {provider}。可选: {list(cls._providers.keys())}"
            )
        
        client_class = cls._providers[provider]
        
        if provider == "ollama":
            kwargs.setdefault("model", os.getenv("OLLAMA_MODEL", "qwen2.5"))
            kwargs.setdefault("host", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        elif provider == "deepseek":
            kwargs.setdefault("model", os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
            kwargs.setdefault("api_key", os.getenv("DEEPSEEK_API_KEY"))
        elif provider == "openai":
            kwargs.setdefault("model", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
            kwargs.setdefault("api_key", os.getenv("OPENAI_API_KEY"))
        
        client = client_class(**kwargs)
        
        if not client.check_available():
            raise RuntimeError(
                f"{client.name} 不可用。请检查配置。"
            )
        
        return client
    
    @classmethod
    def list_providers(cls):
        return list(cls._providers.keys())