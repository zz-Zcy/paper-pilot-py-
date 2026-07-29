import json
from typing import Iterator, Union

import requests

from .base import BaseLLMClient


class OllamaClient(BaseLLMClient):
    def __init__(self, model: str = "qwen2.5", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")
        self.api_url = f"{self.host}/api/chat"
    
    @property
    def name(self) -> str:
        return f"Ollama({self.model})"
    
    def check_available(self) -> bool:
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=5)
            models = [m["name"] for m in r.json().get("models", [])]
            return self.model in models
        except Exception:
            return False
    
    def summarize(self, prompt: str, stream: bool = False) -> Union[str, Iterator[str]]:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位计算机科学领域的资深研究者。请对提供的论文进行结构化总结，用中文输出，保持学术严谨但通俗易懂。",
                },
                {"role": "user", "content": prompt},
            ],
            "stream": stream,
            "options": {
                "temperature": 0.3,
                "num_ctx": 8192,
            },
        }
        
        try:
            response = requests.post(self.api_url, json=payload, stream=stream, timeout=300)
            response.raise_for_status()
            
            if stream:
                return self._stream_response(response)
            return response.json()["message"]["content"]
            
        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"无法连接到 Ollama ({self.host})")
    
    def _stream_response(self, response) -> Iterator[str]:
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "message" in data and "content" in data["message"]:
                    yield data["message"]["content"]