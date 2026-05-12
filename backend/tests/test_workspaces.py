from app.services.workspaces import slugify


def test_slugify_normalizes_workspace_names() -> None:
    assert slugify("  Qalam Growth Team!  ") == "qalam-growth-team"


def test_slugify_returns_empty_string_for_symbols_only() -> None:
    assert slugify("!!!") == ""
