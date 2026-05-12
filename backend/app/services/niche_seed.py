from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.preferences import NicheProfile

NICHE_SEEDS = [
    {
        "slug": "hr-recruiting",
        "name": "HR and Recruiting",
        "audience_types": ["HR leaders", "recruiters", "people operations teams"],
        "content_pillars": ["hiring", "culture", "retention", "candidate experience"],
    },
    {
        "slug": "software-engineering",
        "name": "Software Engineering",
        "audience_types": ["developers", "engineering managers", "technical founders"],
        "content_pillars": ["architecture", "career growth", "shipping", "debugging"],
    },
    {
        "slug": "saas-founder",
        "name": "SaaS Founder",
        "audience_types": ["founders", "operators", "early startup teams"],
        "content_pillars": ["building", "growth", "product", "sales lessons"],
    },
    {
        "slug": "business-consultant",
        "name": "Business Consultant",
        "audience_types": ["business owners", "executives", "operators"],
        "content_pillars": ["strategy", "systems", "operations", "decision making"],
    },
    {
        "slug": "marketing-strategist",
        "name": "Marketing Strategist",
        "audience_types": ["marketers", "founders", "growth teams"],
        "content_pillars": ["positioning", "campaigns", "content", "conversion"],
    },
    {
        "slug": "content-creator",
        "name": "Content Creator",
        "audience_types": ["creators", "solopreneurs", "audience builders"],
        "content_pillars": ["ideas", "workflow", "audience trust", "monetization"],
    },
    {
        "slug": "entrepreneur",
        "name": "Entrepreneur",
        "audience_types": ["entrepreneurs", "builders", "small business owners"],
        "content_pillars": ["lessons", "resilience", "opportunity", "execution"],
    },
    {
        "slug": "career-coach",
        "name": "Career Coach",
        "audience_types": ["job seekers", "professionals", "career switchers"],
        "content_pillars": ["confidence", "interviews", "career clarity", "growth"],
    },
    {
        "slug": "agency-owner",
        "name": "Agency Owner",
        "audience_types": ["agency founders", "service businesses", "client teams"],
        "content_pillars": ["client work", "operations", "positioning", "delivery"],
    },
    {
        "slug": "ecommerce-operator",
        "name": "E-commerce Operator",
        "audience_types": ["store owners", "brand operators", "growth teams"],
        "content_pillars": ["conversion", "retention", "customer insight", "ops"],
    },
    {
        "slug": "real-estate",
        "name": "Real Estate Professional",
        "audience_types": ["buyers", "sellers", "investors", "local networks"],
        "content_pillars": ["market education", "trust", "local insight", "process"],
    },
    {
        "slug": "finance-advisor",
        "name": "Finance Advisor",
        "audience_types": ["professionals", "families", "business owners"],
        "content_pillars": ["planning", "risk", "education", "financial habits"],
    },
]


async def sync_niche_profiles(session: AsyncSession) -> list[NicheProfile]:
    synced: list[NicheProfile] = []
    for seed in NICHE_SEEDS:
        existing = await session.scalar(
            select(NicheProfile).where(NicheProfile.slug == seed["slug"])
        )
        values = {
            **seed,
            "description": f"LinkedIn content strategy for {seed['name']}.",
            "hook_patterns": [
                "A practical lesson from the field",
                "A mistake this audience should avoid",
                "A clear before-and-after insight",
            ],
            "cta_examples": [
                "What would you add?",
                "If this is useful, save it for later.",
                "Share this with someone working on this.",
            ],
            "risky_claims_to_avoid": [
                "Unsupported statistics",
                "Guaranteed business outcomes",
                "Fake client results",
            ],
            "hashtag_guidance": [
                "Use 3 to 5 relevant hashtags",
                "Prefer niche-specific tags over generic viral tags",
            ],
            "is_active": True,
        }
        if existing is None:
            profile = NicheProfile(**values)
            session.add(profile)
            synced.append(profile)
            continue

        for key, value in values.items():
            setattr(existing, key, value)
        synced.append(existing)

    await session.commit()
    return synced
