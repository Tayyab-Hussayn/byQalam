from datetime import datetime

from app.db.models.enums import UsageMetric
from app.services.usage import QUOTA_BY_METRIC, current_month_period


def test_current_month_period_handles_december_rollover() -> None:
    start, end = current_month_period(datetime(2026, 12, 10, 8, 30))

    assert start == datetime(2026, 12, 1)
    assert end == datetime(2027, 1, 1)


def test_quota_mapping_covers_core_billable_metrics() -> None:
    assert QUOTA_BY_METRIC[UsageMetric.AI_GENERATION] == "monthly_ai_generations"
    assert QUOTA_BY_METRIC[UsageMetric.SCHEDULED_POST] == "monthly_scheduled_posts"
    assert QUOTA_BY_METRIC[UsageMetric.PUBLISHED_POST] == "monthly_scheduled_posts"
