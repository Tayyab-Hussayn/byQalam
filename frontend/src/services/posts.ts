import { apiRequest } from "@/lib/api/client";
import type { PostStatus } from "@/types/dashboard";

export interface GeneratePostRequest {
  clientId: string;
  prompt: string;
  tone: string;
  format?: string;
  length?: string;
}

export interface GeneratePostResponse {
  id: string;
  body: string;
  hashtags: string[];
  firstComment?: string;
  antiAiScore?: number;
}

export interface PostRecord {
  id: string;
  workspace_id: string;
  author_user_id: string;
  status: PostStatus;
  source: string;
  niche_slug: string | null;
  title_internal: string | null;
  body: string;
  hashtags: string[];
  first_comment: string | null;
  scheduled_for: string | null;
  timezone: string;
  linkedin_target_type: string | null;
  linkedin_target_urn: string | null;
  linkedin_post_urn: string | null;
  rejection_reason: string | null;
  failure_reason: string | null;
}

export interface PostListResponse {
  posts: PostRecord[];
}

export interface PostScheduleRequest {
  scheduled_for: string;
  timezone?: string;
  linkedin_target_type?: "member" | "organization" | null;
  linkedin_target_urn?: string | null;
}

export function generatePost(
  payload: GeneratePostRequest,
  signal?: AbortSignal,
) {
  return apiRequest<GeneratePostResponse>(
    "/posts/generate",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    signal,
  );
}

export function listWorkspacePosts(
  workspaceId: string,
  params: { limit?: number; offset?: number; status?: PostStatus } = {},
  signal?: AbortSignal,
) {
  const query = new URLSearchParams();
  if (params.limit !== undefined) query.set("limit", String(params.limit));
  if (params.offset !== undefined) query.set("offset", String(params.offset));
  if (params.status) query.set("status", params.status);

  const suffix = query.toString() ? `?${query.toString()}` : "";
  return apiRequest<PostListResponse>(
    `/workspaces/${workspaceId}/posts${suffix}`,
    {},
    signal,
  );
}

export function scheduleWorkspacePost(
  workspaceId: string,
  postId: string,
  payload: PostScheduleRequest,
  signal?: AbortSignal,
) {
  return apiRequest<PostRecord>(
    `/workspaces/${workspaceId}/posts/${postId}/schedule`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    signal,
  );
}

export function cancelWorkspacePost(
  workspaceId: string,
  postId: string,
  signal?: AbortSignal,
) {
  return apiRequest<PostRecord>(
    `/workspaces/${workspaceId}/posts/${postId}/cancel`,
    {
      method: "POST",
    },
    signal,
  );
}
