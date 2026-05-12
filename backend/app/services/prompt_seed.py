from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.ai import PromptTemplate

PROMPT_TEMPLATE_SEEDS = [
    {
        "name": "linkedin_post",
        "version": "v1",
        "description": "Default LinkedIn text post generation prompt.",
        "system_prompt": (
            "You are Qalam's LinkedIn content strategist. Generate useful, "
            "specific, human posts without fake claims or unsupported stats."
        ),
        "user_prompt_template": (
            "Prompt: {prompt}\nNiche: {niche_slug}\nAudience: {target_audience}\n"
            "Tone: {tone}\nLanguage: {language}"
        ),
    }
]


async def sync_prompt_templates(session: AsyncSession) -> list[PromptTemplate]:
    synced: list[PromptTemplate] = []
    for seed in PROMPT_TEMPLATE_SEEDS:
        existing = await session.scalar(
            select(PromptTemplate).where(
                PromptTemplate.name == seed["name"],
                PromptTemplate.version == seed["version"],
            )
        )
        if existing is None:
            template = PromptTemplate(**seed)
            session.add(template)
            synced.append(template)
            continue

        for key, value in seed.items():
            setattr(existing, key, value)
        existing.is_active = True
        synced.append(existing)

    await session.commit()
    return synced
