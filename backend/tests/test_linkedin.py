from uuid import uuid4

from app.db.models.enums import LinkedinTargetType, PostStatus
from app.db.models.linkedin import LinkedinConnection
from app.db.models.post import Post
from app.services.linkedin import build_text_post_payload, hash_oauth_state


def test_oauth_state_hash_is_stable_and_not_raw_value() -> None:
    raw_state = "state-token"

    hashed = hash_oauth_state(raw_state)

    assert hashed == hash_oauth_state(raw_state)
    assert hashed != raw_state
    assert len(hashed) == 64


def test_build_text_post_payload_uses_rest_posts_shape() -> None:
    connection = LinkedinConnection(
        workspace_id=uuid4(),
        connected_by_user_id=uuid4(),
        target_type=LinkedinTargetType.MEMBER,
        target_urn="urn:li:person:123",
        access_token_encrypted="encrypted",
        scopes=[],
        token_key_id="local",
        metadata_json={},
    )
    post = Post(
        workspace_id=uuid4(),
        author_user_id=uuid4(),
        body="Qalam generated post",
        hashtags=["#linkedin"],
        status=PostStatus.APPROVED,
    )

    payload = build_text_post_payload(post, connection)

    assert payload["author"] == "urn:li:person:123"
    assert payload["commentary"] == "Qalam generated post\n\n#linkedin"
    assert payload["lifecycleState"] == "PUBLISHED"
    assert payload["distribution"]["feedDistribution"] == "MAIN_FEED"
