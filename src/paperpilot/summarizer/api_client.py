import os
from typing import Iterator, Union

import requests

from .base import BaseLLMClient


class DeepSeekClient(BaseLLMClient):
    API_URL = "https://api.deepseek.com/chat/completions"
    
    def __init__(self, api_key: str = None, model: str = "deepseek-chat"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = model
    
    @property
    def name(self) -> str:
        return f"DeepSeek({self.model})"
    
    def check_available(self) -> bool:
        return bool(self.api_key)
    
    def summarize(self, prompt: str, stream: bool = False) -> Union[str, Iterator[str]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位计算机科学领域的资深研究者。请对论文进行结构化总结，用中文输出。",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "stream": stream,
        }
        
        response = requests.post(self.API_URL, headers=headers, json=payload, stream=stream, timeout=120)
        response.raise_for_status()
        
        if stream:
            return self._stream_response(response)
        return response.json()["choices"][0]["message"]["content"]
    
    def _stream_response(self, response) -> Iterator[str]:
        for line in response.iter_lines():
            if line and line.startswith(b"data: "):
                data = line[6:].decode("utf-8")
                if data == "[DONE]":
                    break
                import json
                chunk = json.loads(data)
                if chunk["choices"][0]["delta"].get("content"):
                    yield chunk["choices"][0]["delta"]["content"]


class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini", base_url: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url or "https://api.openai.com/v1"
    
    @property
    def name(self) -> str:
        return f"OpenAI({self.model})"
    
    def check_available(self) -> bool:
        return bool(self.api_key)
    
    def summarize(self, prompt: str, stream: bool = False) -> Union[str, Iterator[str]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位计算机科学领域的资深研究者。请对论文进行结构化总结，用中文输出。",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "stream": stream,
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            stream=stream,
            timeout=120,
        )
        response.raise_for_status()
        
        if stream:
            return self._stream_response(response)
        return response.json()["choices"][0]["message"]["content"]
    
    def _stream_response(self, response) -> Iterator[str]:
        for line in response.iter_lines():
            if line and line.startswith(b"data: "):
                data = line[6:].decode("utf-8")
                if data == "[DONE]":
                    break
                import json
                chunk = json.loads(data)
                if chunk["choices"][0]["delta"].get("content"):
                    yield chunk["choices"][0]["delta"]["content"]