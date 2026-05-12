import { apiRequest } from "@/lib/api/client";
import type { UsageSummary } from "./dashboard";

export interface BillingPlan {
  slug: string;
  name: string;
  sort_order: number;
  stripe_price_id: string | null;
  quotas: {
    monthly_ai_generations: number;
    monthly_scheduled_posts: number;
    max_workspaces: number;
    max_members: number;
    max_linkedin_connections: number;
    media_storage_mb: number;
  };
}

export type SubscriptionStatus =
  | "trialing"
  | "active"
  | "past_due"
  | "canceled"
  | "paused"
  | "incomplete";

export interface BillingSubscription {
  workspace_id: string;
  plan_slug: string | null;
  status: SubscriptionStatus;
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  current_period_start: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
}

export interface BillingSummary {
  workspace_id: string;
  plan: BillingPlan | null;
  subscription: BillingSubscription | null;
  usage: UsageSummary;
}

export interface BillingCheckoutRequest {
  plan_slug: string;
  success_url: string;
  cancel_url: string;
}

export interface BillingPortalRequest {
  return_url: string;
}

export interface BillingSessionResponse {
  url: string;
  provider_session_id: string;
}

export function readBillingSummary(workspaceId: string, signal?: AbortSignal) {
  return apiRequest<BillingSummary>(`/billing/workspaces/${workspaceId}`, {}, signal);
}

export function createCheckoutSession(
  workspaceId: string,
  payload: BillingCheckoutRequest,
  signal?: AbortSignal,
) {
  return apiRequest<BillingSessionResponse>(
    `/billing/workspaces/${workspaceId}/checkout`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    signal,
  );
}

export function createPortalSession(
  workspaceId: string,
  payload: BillingPortalRequest,
  signal?: AbortSignal,
) {
  return apiRequest<BillingSessionResponse>(
    `/billing/workspaces/${workspaceId}/portal`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    signal,
  );
}
