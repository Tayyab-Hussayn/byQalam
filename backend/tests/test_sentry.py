from app.core.sentry import configure_sentry


def test_configure_sentry_is_noop_without_dsn() -> None:
    configure_sentry()
