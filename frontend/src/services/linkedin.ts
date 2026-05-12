import { apiRequest } from "@/lib/api/client";

export type LinkedinTargetType = "person" | "organization";
export type LinkedinConnectionStatus =
  | "connected"
  | "expired"
  | "revoked"
  | "failed"
  | "error";

export interface LinkedinConnectRequest {
  redirect_after?: string | null;
}

export interface LinkedinConnectResponse {
  authorization_url: string;
  expires_at: string;
}

export interface LinkedinConnection {
  id: string;
  workspace_id: string;
  target_type: LinkedinTargetType;
  target_urn: string;
  display_name: string | null;
  status: LinkedinConnectionStatus;
  token_expires_at: string | null;
  scopes: string[];
  created_at: string;
  updated_at: string;
}

export interface LinkedinConnectionListResponse {
  connections: LinkedinConnection[];
}

export interface LinkedinOAuthCallbackResponse {
  connection: LinkedinConnection;
  redirect_after: string | null;
}

export interface LinkedinPublishNowResponse {
  post_id: string;
  publish_attempt_id: string;
  linkedin_post_urn: string;
}

export function createLinkedinConnectUrl(
  workspaceId: string,
  payload: LinkedinConnectRequest,
  signal?: AbortSignal,
) {
  return apiRequest<LinkedinConnectResponse>(
    `/linkedin/workspaces/${workspaceId}/connect`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    signal,
  );
}

export function readLinkedinConnections(
  workspaceId: string,
  signal?: AbortSignal,
) {
  return apiRequest<LinkedinConnectionListResponse>(
    `/linkedin/workspaces/${workspaceId}/connections`,
    {},
    signal,
  );
}

export function disconnectLinkedinConnection(
  workspaceId: string,
  connectionId: string,
  signal?: AbortSignal,
) {
  return apiRequest<LinkedinConnection>(
    `/linkedin/workspaces/${workspaceId}/connections/${connectionId}`,
    {
      method: "DELETE",
    },
    signal,
  );
}

export function publishLinkedinPostNow(
  workspaceId: string,
  postId: string,
  connectionId: string,
  signal?: AbortSignal,
) {
  return apiRequest<LinkedinPublishNowResponse>(
    `/linkedin/workspaces/${workspaceId}/posts/${postId}/publish-now?connection_id=${encodeURIComponent(connectionId)}`,
    {
      method: "POST",
    },
    signal,
  );
}
