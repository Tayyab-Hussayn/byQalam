export type DashboardView =
  | "landing"
  | "dashboard"
  | "writer"
  | "voice"
  | "analytics"
  | "integrations"
  | "settings";

export type PostStatus =
  | "posted"
  | "published"
  | "scheduled"
  | "draft"
  | "generated"
  | "needs_review"
  | "approved"
  | "publishing"
  | "rejected"
  | "failed"
  | "cancelled";

export interface PostSummary {
  id: string;
  status: PostStatus;
  text: string;
  metrics: string[];
}

export interface MetricCard {
  label: string;
  value: string;
  change: string;
}

export interface QuickAction {
  icon: string;
  label: string;
  sublabel: string;
  prompt: string;
}
