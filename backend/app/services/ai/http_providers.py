import json
from typing import Any

import httpx

from app.core.config import settings
from app.services.ai.providers import GeneratedPost, GenerationContext


class BaseHttpGenerationProvider:
    provider_name = "http"
    model_name = settings.ai_default_model

    def __init__(self, provider_name: str, model_name: str | None = None) -> None:
        self.provider_name = provider_name
        self.model_name = model_name or settings.ai_default_model

    async def generate_post(self, context: GenerationContext) -> GeneratedPost:
        raise NotImplementedError

    def _finalize(
        self,
        body: str,
        hashtags: list[str],
        first_comment: str | None,
    ) -> GeneratedPost:
        return GeneratedPost(
            body=body.strip(),
            hashtags=hashtags[:5],
            first_comment=first_comment.strip() if first_comment else None,
            quality_score=self._quality_score(body, hashtags),
            tokens_input=max(1, len(body.split()) // 2),
            tokens_output=max(1, len(body.split())),
            estimated_cost_cents=self._estimated_cost_cents(body),
        )

    def _quality_score(self, body: str, hashtags: list[str]) -> int:
        base = 72
        if len(body) > 500:
            base += 8
        if len(hashtags) >= 3:
            base += 5
        return min(96, base)

    def _estimated_cost_cents(self, body: str) -> int:
        return max(1, len(body.split()) // 120)


class OpenAIProvider(BaseHttpGenerationProvider):
    provider_name = "openai"

    async def generate_post(self, context: GenerationContext) -> GeneratedPost:
        payload = _build_json_prompt(context)
        async with httpx.AsyncClient(
            timeout=settings.ai_request_timeout_seconds,
        ) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": self.model_name,
                    "input": payload,
                    "text": {"format": {"type": "json_object"}},
                },
            )
        data = _ensure_ok(response)
        parsed = _parse_json_output(data, context)
        return self._finalize(
            parsed["body"],
            parsed["hashtags"],
            parsed.get("first_comment"),
        )


class AnthropicProvider(BaseHttpGenerationProvider):
    provider_name = "anthropic"

    async def generate_post(self, context: GenerationContext) -> GeneratedPost:
        payload = _build_json_prompt(context)
        async with httpx.AsyncClient(
            timeout=settings.ai_request_timeout_seconds,
        ) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key or "",
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": self.model_name,
                    "max_tokens": 1200,
                    "messages": [{"role": "user", "content": payload}],
                },
            )
        data = _ensure_ok(response)
        parsed = _parse_json_output(data, context)
        return self._finalize(
            parsed["body"],
            parsed["hashtags"],
            parsed.get("first_comment"),
        )


class GroqProvider(BaseHttpGenerationProvider):
    provider_name = "groq"

    async def generate_post(self, context: GenerationContext) -> GeneratedPost:
        return await _openai_compatible_generate(
            base_url="https://api.groq.com/openai/v1/chat/completions",
            api_key=settings.groq_api_key or "",
            context=context,
            model=self.model_name,
            provider=self,
        )


class MistralProvider(BaseHttpGenerationProvider):
    provider_name = "mistral"

    async def generate_post(self, context: GenerationContext) -> GeneratedPost:
        return await _openai_compatible_generate(
            base_url="https://api.mistral.ai/v1/chat/completions",
            api_key=settings.mistral_api_key or "",
            context=context,
            model=self.model_name,
            provider=self,
        )


class OpenCodeProvider(BaseHttpGenerationProvider):
    provider_name = "opencode"

    async def generate_post(self, context: GenerationContext) -> GeneratedPost:
        return await _openai_compatible_generate(
            base_url="https://opencode.ai/zen/v1/chat/completions",
            api_key=settings.opencode_api_key or "",
            context=context,
            model=self.model_name,
            provider=self,
        )


class GoogleProvider(BaseHttpGenerationProvider):
    provider_name = "google"

    async def generate_post(self, context: GenerationContext) -> GeneratedPost:
        payload = _build_json_prompt(context)
        async with httpx.AsyncClient(
            timeout=settings.ai_request_timeout_seconds,
        ) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent",
                params={"key": settings.google_ai_api_key or ""},
                json={
                    "contents": [
                        {"parts": [{"text": payload}]},
                    ]
                },
            )
        data = _ensure_ok(response)
        parsed = _parse_json_output(data, context)
        return self._finalize(
            parsed["body"],
            parsed["hashtags"],
            parsed.get("first_comment"),
        )


async def _openai_compatible_generate(
    base_url: str,
    api_key: str,
    context: GenerationContext,
    model: str,
    provider: BaseHttpGenerationProvider,
) -> GeneratedPost:
    payload = _build_json_prompt(context)
    async with httpx.AsyncClient(
        timeout=settings.ai_request_timeout_seconds,
    ) as client:
        response = await client.post(
            base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": payload}],
                "temperature": 0.8,
                "response_format": {"type": "json_object"},
            },
        )
    data = _ensure_ok(response)
    parsed = _parse_json_output(data, context)
    return provider._finalize(
        parsed["body"],
        parsed["hashtags"],
        parsed.get("first_comment"),
    )


def _build_json_prompt(context: GenerationContext) -> str:
    return (
        "Write a polished LinkedIn post as JSON only with keys body, hashtags, "
        "first_comment. Use the context below.\n"
        f"{json.dumps(context.__dict__, ensure_ascii=True)}"
    )


def _ensure_ok(response: httpx.Response) -> dict[str, Any]:
    if response.status_code >= 400:
        raise RuntimeError(response.text[:1000])
    return response.json()


def _parse_json_output(
    data: dict[str, Any],
    context: GenerationContext,
) -> dict[str, Any]:
    raw_text = (
        data.get("output_text")
        or data.get("content")
        or data.get("text")
        or data.get("response")
    )
    if isinstance(raw_text, list):
        raw_text = "".join(
            chunk.get("text", "") if isinstance(chunk, dict) else str(chunk)
            for chunk in raw_text
        )
    if isinstance(raw_text, dict):
        raw_text = raw_text.get("text") or raw_text.get("body")
    if not raw_text:
        raw_text = json.dumps(data)

    try:
        parsed = json.loads(raw_text)
    except Exception:
        parsed = {
            "body": raw_text,
            "hashtags": _fallback_hashtags(context),
            "first_comment": None,
        }
    if "hashtags" not in parsed or not isinstance(parsed["hashtags"], list):
        parsed["hashtags"] = _fallback_hashtags(context)
    if "body" not in parsed:
        parsed["body"] = raw_text
    return parsed


def _fallback_hashtags(context: GenerationContext) -> list[str]:
    tags = ["#linkedin", "#content", "#ai"]
    if context.niche_slug:
        tags.insert(0, f"#{context.niche_slug.replace('-', '')}")
    return tags[:5]
