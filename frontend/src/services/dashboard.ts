import { apiRequest } from "@/lib/api/client";
import type { AuthUser } from "@/types/auth";
import type { PostStatus } from "@/types/dashboard";
import { readBillingSummary, type BillingSummary } from "@/services/billing";
import { listWorkspacePosts, type PostRecord } from "@/services/posts";

export type WorkspaceRole = "owner" | "admin" | "editor" | "viewer";

export interface WorkspaceSummary {
  id: string;
  name: string;
  slug: string;
  timezone: string;
  role: WorkspaceRole | null;
}

export interface MeResponse {
  user: AuthUser;
  workspaces: WorkspaceSummary[];
}

export interface UsageItem {
  metric: string;
  used: number;
  limit: number | null;
}

export interface UsageSummary {
  plan_slug: string;
  period_start: string;
  period_end: string;
  items: UsageItem[];
}

export interface GeneratedPostRecord {
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

export interface GenerateWorkspacePostRequest {
  prompt: string;
  tone?: string | null;
  niche_slug?: string | null;
  title_internal?: string | null;
}

export interface GenerateWorkspacePostResponse {
  post: GeneratedPostRecord;
  generation_run_id: string;
  quality_score: number | null;
}

export interface WorkspaceContext {
  user: AuthUser;
  workspaces: WorkspaceSummary[];
  activeWorkspace: WorkspaceSummary | null;
  usage: UsageSummary | null;
}

export interface DashboardSnapshot extends WorkspaceContext {
  billing: BillingSummary | null;
  recentPosts: PostRecord[];
}

export async function readWorkspaceContext(
  signal?: AbortSignal,
): Promise<WorkspaceContext> {
  const me = await apiRequest<MeResponse>("/me", {}, signal);
  const activeWorkspace = me.workspaces[0] ?? null;

  let usage: UsageSummary | null = null;
  if (activeWorkspace) {
    usage = await apiRequest<UsageSummary>(
      `/workspaces/${activeWorkspace.id}/usage`,
      {},
      signal,
    );
  }

  return {
    user: me.user,
    workspaces: me.workspaces,
    activeWorkspace,
    usage,
  };
}

export function generateWorkspacePost(
  workspaceId: string,
  payload: GenerateWorkspacePostRequest,
  signal?: AbortSignal,
) {
  return apiRequest<GenerateWorkspacePostResponse>(
    `/workspaces/${workspaceId}/generation/generate-post`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    signal,
  );
}

export async function readDashboardSnapshot(
  signal?: AbortSignal,
): Promise<DashboardSnapshot> {
  const context = await readWorkspaceContext(signal);
  if (!context.activeWorkspace) {
    return {
      ...context,
      billing: null,
      recentPosts: [],
    };
  }

  const [billing, posts] = await Promise.all([
    readBillingSummary(context.activeWorkspace.id, signal).catch(() => null),
    listWorkspacePosts(context.activeWorkspace.id, { limit: 4 }, signal).catch(
      () => ({ posts: [] } as { posts: PostRecord[] }),
    ),
  ]);

  return {
    ...context,
    billing,
    recentPosts: posts.posts,
  };
}
