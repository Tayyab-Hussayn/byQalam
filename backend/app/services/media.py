from math import ceil

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import UsageMetric
from app.db.models.post import Post, PostMedia
from app.schemas.media import PostMediaCreateRequest
from app.services.usage import assert_quota_available, record_usage


async def attach_post_media(
    session: AsyncSession,
    post: Post,
    payload: PostMediaCreateRequest,
) -> PostMedia:
    size_bytes = payload.size_bytes or 0
    usage_amount = max(1, ceil(size_bytes / (1024 * 1024))) if size_bytes else 1
    await assert_quota_available(
        session,
        post.workspace_id,
        UsageMetric.MEDIA_STORAGE_MB,
        amount=usage_amount,
    )
    media = PostMedia(
        post_id=post.id,
        storage_path=payload.storage_path,
        media_type=payload.media_type,
        original_filename=payload.original_filename,
        size_bytes=payload.size_bytes,
    )
    session.add(media)
    await record_usage(
        session,
        post.workspace_id,
        UsageMetric.MEDIA_STORAGE_MB,
        amount=usage_amount,
        metadata={
            "post_id": str(post.id),
            "storage_path": payload.storage_path,
            "media_type": payload.media_type,
        },
    )
    await session.commit()
    await session.refresh(media)
    return media
