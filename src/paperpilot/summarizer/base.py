from abc import ABC, abstractmethod
from typing import Iterator, Union


class BaseLLMClient(ABC):
    """LLM 客户端抽象基类"""
    
    @abstractmethod
    def summarize(self, prompt: str, stream: bool = False) -> Union[str, Iterator[str]]:
        pass
    
    @abstractmethod
    def check_available(self) -> bool:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
