from abc import ABC, abstractmethod

import httpx

from .models import SearchResult


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, prompt: str, results: list[SearchResult]) -> str:
        raise NotImplementedError


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def generate(self, system_prompt: str, prompt: str, results: list[SearchResult]) -> str:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "temperature": 0.1,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


class ContextOnlyProvider(LLMProvider):
    async def generate(self, system_prompt: str, prompt: str, results: list[SearchResult]) -> str:
        if not results:
            return "The indexed repository does not contain enough information to answer this question."
        descriptions = [
            f"- `{item.chunk.file}` lines {item.chunk.start_line}-{item.chunk.end_line}: "
            f"{item.chunk.type} `{item.chunk.name}`"
            for item in results
        ]
        return (
            "No LLM API key is configured. These are the most relevant indexed code sections:\n\n"
            + "\n".join(descriptions)
            + "\n\nConfigure `GROQ_API_KEY`, `OPENAI_API_KEY`, or `XAI_API_KEY` for a synthesized explanation."
        )


def create_llm_provider(settings) -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider in {"auto", "groq"} and settings.groq_api_key:
        return OpenAICompatibleProvider(
            settings.groq_api_key,
            settings.groq_model,
            "https://api.groq.com/openai/v1",
        )
    if provider in {"auto", "openai"} and settings.openai_api_key:
        return OpenAICompatibleProvider(settings.openai_api_key, settings.openai_model, "https://api.openai.com/v1")
    if provider in {"auto", "grok", "xai"} and settings.xai_api_key:
        return OpenAICompatibleProvider(settings.xai_api_key, settings.xai_model, "https://api.x.ai/v1")
    return ContextOnlyProvider()
