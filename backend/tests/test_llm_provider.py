from types import SimpleNamespace

from backend.llm_provider import OpenAICompatibleProvider, create_llm_provider


def test_creates_groq_provider() -> None:
    settings = SimpleNamespace(
        llm_provider="groq",
        groq_api_key="test-key",
        groq_model="llama-3.3-70b-versatile",
        openai_api_key=None,
        openai_model="gpt-4o-mini",
        xai_api_key=None,
        xai_model="grok-3-mini",
    )

    provider = create_llm_provider(settings)

    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider.base_url == "https://api.groq.com/openai/v1"
    assert provider.model == "llama-3.3-70b-versatile"
