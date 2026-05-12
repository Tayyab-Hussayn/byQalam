from app.services.ai.providers import GeneratedPost, GenerationContext


class MockContentGenerationProvider:
    provider_name = "mock"
    model_name = "mock-qalam-v1"

    async def generate_post(self, context: GenerationContext) -> GeneratedPost:
        niche = context.niche_slug or "professional growth"
        tone = context.tone or "clear"
        audience = context.target_audience or "LinkedIn audience"
        body = (
            f"{context.prompt.strip()}\n\n"
            f"Here is a {tone} LinkedIn post for {audience} in the "
            f"{niche} space.\n\n"
            "The strongest content starts with a real point of view, then "
            "turns that point into a practical lesson people can use today.\n\n"
            "Keep it specific. Keep it useful. Keep it human."
        )
        hashtags = _hashtags_from_context(context)
        return GeneratedPost(
            body=body,
            hashtags=hashtags,
            first_comment="What would you add from your experience?",
            quality_score=82,
            tokens_input=max(1, len(context.prompt.split())),
            tokens_output=max(1, len(body.split())),
            estimated_cost_cents=0,
        )


def _hashtags_from_context(context: GenerationContext) -> list[str]:
    base = ["#linkedin", "#content", "#leadership"]
    if context.niche_slug:
        base.insert(0, f"#{context.niche_slug.replace('-', '')}")
    return base[:5]
