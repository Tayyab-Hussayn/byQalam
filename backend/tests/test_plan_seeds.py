from app.core.config import Settings
from app.services.plans import build_plan_seeds


def test_build_plan_seeds_maps_env_defaults_to_plan_quotas() -> None:
    settings = Settings(
        _env_file=None,
        free_monthly_ai_generations=7,
        pro_monthly_ai_generations=900,
        stripe_price_pro="price_pro_test",
    )

    plans = {plan.slug: plan for plan in build_plan_seeds(settings)}

    assert plans["free"].quotas.monthly_ai_generations == 7
    assert plans["pro"].quotas.monthly_ai_generations == 900
    assert plans["pro"].stripe_price_id == "price_pro_test"
    assert plans["agency"].quotas.max_workspaces == settings.agency_max_workspaces
