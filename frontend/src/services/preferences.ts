import { apiRequest } from "@/lib/api/client";

export interface ContentPreference {
  id: string;
  workspace_id: string;
  niche_slug: string | null;
  target_audience: string | null;
  content_goals: string[];
  tone: string | null;
  language: string;
  post_style: string | null;
  cta_preference: string | null;
  hashtag_policy: string | null;
  emoji_policy: string | null;
  topics_to_avoid: string[];
  preferred_post_length: string | null;
}

export interface ContentPreferenceInput {
  niche_slug?: string | null;
  target_audience?: string | null;
  content_goals?: string[];
  tone?: string | null;
  language?: string;
  post_style?: string | null;
  cta_preference?: string | null;
  hashtag_policy?: string | null;
  emoji_policy?: string | null;
  topics_to_avoid?: string[];
  preferred_post_length?: string | null;
}

export interface VoiceProfile {
  id: string;
  workspace_id: string;
  summary: string | null;
  traits: string[];
  banned_phrases: string[];
  confidence_score: number;
  sample_count: number;
}

export interface VoiceProfileInput {
  summary?: string | null;
  traits?: string[];
  banned_phrases?: string[];
  confidence_score?: number;
}

export interface WritingSample {
  id: string;
  workspace_id: string;
  user_id: string;
  title: string | null;
  body: string;
  source: string | null;
}

export interface WritingSampleInput {
  title?: string | null;
  body: string;
  source?: string | null;
}

export interface NicheProfile {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  audience_types: string[];
  content_pillars: string[];
  hook_patterns: string[];
  cta_examples: string[];
  risky_claims_to_avoid: string[];
  hashtag_guidance: string[];
}

export interface NicheProfileListResponse {
  niches: NicheProfile[];
}

export interface WritingSampleListResponse {
  samples: WritingSample[];
}

export function readNicheProfiles(signal?: AbortSignal) {
  return apiRequest<NicheProfileListResponse>("/niches", {}, signal);
}

export function readContentPreferences(workspaceId: string, signal?: AbortSignal) {
  return apiRequest<ContentPreference | null>(
    `/workspaces/${workspaceId}/preferences`,
    {},
    signal,
  );
}

export function saveContentPreferences(
  workspaceId: string,
  payload: ContentPreferenceInput,
  signal?: AbortSignal,
) {
  return apiRequest<ContentPreference>(
    `/workspaces/${workspaceId}/preferences`,
    {
      method: "PUT",
      body: JSON.stringify(payload),
    },
    signal,
  );
}

export function readVoiceProfile(workspaceId: string, signal?: AbortSignal) {
  return apiRequest<VoiceProfile | null>(
    `/workspaces/${workspaceId}/voice-profile`,
    {},
    signal,
  );
}

export function saveVoiceProfile(
  workspaceId: string,
  payload: VoiceProfileInput,
  signal?: AbortSignal,
) {
  return apiRequest<VoiceProfile>(
    `/workspaces/${workspaceId}/voice-profile`,
    {
      method: "PUT",
      body: JSON.stringify(payload),
    },
    signal,
  );
}

export function readWritingSamples(
  workspaceId: string,
  signal?: AbortSignal,
) {
  return apiRequest<WritingSampleListResponse>(
    `/workspaces/${workspaceId}/writing-samples`,
    {},
    signal,
  );
}

export function addWritingSample(
  workspaceId: string,
  payload: WritingSampleInput,
  signal?: AbortSignal,
) {
  return apiRequest<WritingSample>(
    `/workspaces/${workspaceId}/writing-samples`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    signal,
  );
}
