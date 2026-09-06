import logging
from abc import ABC, abstractmethod

import httpx

from .models import SearchResult

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, prompt: str, results: list[SearchResult]) -> str:
        raise NotImplementedError


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, base_url: str, fallback_models: list[str] | None = None) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.fallback_models = fallback_models or []

    async def _try_generate(self, client: httpx.AsyncClient, model: str, system_prompt: str, prompt: str) -> str:
        response = await client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": model,
                "temperature": 0.1,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    async def generate(self, system_prompt: str, prompt: str, results: list[SearchResult]) -> str:
        models_to_try = [self.model] + [m for m in self.fallback_models if m != self.model]
        last_error = None

        async with httpx.AsyncClient(timeout=90) as client:
            for model in models_to_try:
                try:
                    return await self._try_generate(client, model, system_prompt, prompt)
                except Exception as exc:
                    last_error = exc
                    logger.warning(f"Failed to generate answer with model '{model}': {exc}")

        logger.error(f"All LLM generation attempts failed: {last_error}", exc_info=True)
        if not results:
            return f"Unable to reach LLM provider ({last_error}) and no indexed code sections were found."

        descriptions = [
            f"- `{item.chunk.file}` lines {item.chunk.start_line}-{item.chunk.end_line}: "
            f"{item.chunk.type} `{item.chunk.name}`"
            for item in results
        ]
        return (
            f"⚠️ *Note: LLM provider request failed ({last_error}). Showing relevant indexed code sections:*\n\n"
            + "\n".join(descriptions)
        )


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
            fallback_models=["openai/gpt-oss-120b", "openai/gpt-oss-20b", "groq/compound-mini", "groq/compound"],
        )
    if provider in {"auto", "openai"} and settings.openai_api_key:
        return OpenAICompatibleProvider(
            settings.openai_api_key,
            settings.openai_model,
            "https://api.openai.com/v1",
            fallback_models=["gpt-4o-mini", "gpt-4o"],
        )
    if provider in {"auto", "grok", "xai"} and settings.xai_api_key:
        return OpenAICompatibleProvider(
            settings.xai_api_key,
            settings.xai_model,
            "https://api.x.ai/v1",
            fallback_models=["grok-3-mini", "grok-2"],
        )
    return ContextOnlyProvider()
