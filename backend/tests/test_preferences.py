from app.services.niche_seed import NICHE_SEEDS


def test_niche_seed_contains_required_initial_niches() -> None:
    slugs = {seed["slug"] for seed in NICHE_SEEDS}

    assert "hr-recruiting" in slugs
    assert "software-engineering" in slugs
    assert "saas-founder" in slugs
    assert len(slugs) >= 10
