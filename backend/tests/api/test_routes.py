from app.main import create_app


def test_auth_routes_are_registered() -> None:
    paths = {route.path for route in create_app().routes}

    assert "/api/v1/me" in paths
    assert "/api/v1/workspaces" in paths
    assert "/api/v1/niches" in paths
    assert "/api/v1/workspaces/{workspace_id}/preferences" in paths
    assert "/api/v1/workspaces/{workspace_id}/voice-profile" in paths
    assert "/api/v1/workspaces/{workspace_id}/writing-samples" in paths
    assert "/api/v1/workspaces/{workspace_id}/members" in paths
    assert "/api/v1/workspaces/{workspace_id}/invites" in paths
    assert "/api/v1/workspaces/invites/accept" in paths
    assert "/api/v1/workspaces/{workspace_id}/members/{member_id}" in paths
    assert "/api/v1/workspaces/{workspace_id}/posts" in paths
    assert "/api/v1/workspaces/{workspace_id}/posts/{post_id}/media" in paths
    assert "/api/v1/workspaces/{workspace_id}/posts/{post_id}" in paths
    assert "/api/v1/workspaces/{workspace_id}/posts/{post_id}/approve" in paths
    assert "/api/v1/workspaces/{workspace_id}/posts/{post_id}/schedule" in paths
    assert "/api/v1/workspaces/{workspace_id}/generation/generate-post" in paths
    assert (
        "/api/v1/workspaces/{workspace_id}/generation/posts/{post_id}/regenerate"
        in paths
    )
    assert "/api/v1/linkedin/workspaces/{workspace_id}/connect" in paths
    assert "/api/v1/linkedin/oauth/callback" in paths
    assert "/api/v1/linkedin/workspaces/{workspace_id}/connections" in paths
    assert (
        "/api/v1/linkedin/workspaces/{workspace_id}/posts/{post_id}/publish-now"
        in paths
    )
    assert "/api/v1/billing/workspaces/{workspace_id}" in paths
    assert "/api/v1/billing/workspaces/{workspace_id}/checkout" in paths
    assert "/api/v1/billing/workspaces/{workspace_id}/portal" in paths
    assert "/api/v1/billing/webhook" in paths
    assert "/api/v1/workspaces/{workspace_id}/usage" in paths
