"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError } from "@/lib/api/client";
import { supabase } from "@/lib/auth/supabase";
import { DASHBOARD_METRICS, GENERATED_HASHTAGS, RECENT_POSTS } from "@/features/dashboard/data/dashboardMock";
import {
  generateWorkspacePost,
  readDashboardSnapshot,
  type DashboardSnapshot,
  type UsageItem,
} from "@/services/dashboard";
import {
  addWritingSample,
  readContentPreferences,
  readNicheProfiles,
  readVoiceProfile,
  readWritingSamples,
  saveContentPreferences,
  saveVoiceProfile,
  type ContentPreference,
  type NicheProfile,
  type WritingSample,
  type VoiceProfile,
  type VoiceProfileInput,
} from "@/services/preferences";
import {
  cancelWorkspacePost,
  scheduleWorkspacePost,
} from "@/services/posts";
import {
  createLinkedinConnectUrl,
  disconnectLinkedinConnection,
  publishLinkedinPostNow,
  readLinkedinConnections,
  type LinkedinConnection,
} from "@/services/linkedin";
import { createCheckoutSession, createPortalSession } from "@/services/billing";
import type { DashboardView, MetricCard, PostSummary } from "@/types/dashboard";
import {
  AnalyticsView,
  DashboardView as DashboardOverviewView,
  LandingView,
  IntegrationsView,
  SettingsView,
  VoiceView,
  WriterView,
} from "./components/DashboardViews";
import type {
  SettingsDraft,
  VoiceDraft,
  WritingSampleDraft,
} from "./components/DashboardViews";
import { Notification } from "./components/Notification";
import { OnboardingModal } from "./components/OnboardingModal";
import { Sidebar } from "./components/Sidebar";
import { Topbar } from "./components/Topbar";
import { onboardingSteps } from "./dashboardConfig";
import { dashboardStyles } from "./dashboardStyles";

const DEFAULT_SELECTED_TAGS = [
  "Talent Acquisition",
  "People Strategy",
  "Culture Building",
  "Brand Building",
  "Thought Leadership",
  "thrilled to share",
  "game-changing",
  "paradigm shift",
  "delve into",
] as const;

const LOCAL_GENERATED_POST = `Nobody tells you this when you start leading people.

The hardest part is not making decisions.

It is making them while knowing someone will misunderstand you.

I used to think leadership meant being liked.

Now I think it means being clear enough that people can trust you even when they disagree.

The best leaders I know do three things well:

They explain the why.
They own the tradeoff.
They stay human after the decision.

That is the part most leadership books skip.

What is one leadership lesson you had to learn the hard way?`;

const USAGE_METRIC_ORDER = [
  "ai_generations",
  "scheduled_posts",
  "published_posts",
  "linkedin_connections",
];

const USAGE_METRIC_LABELS: Record<string, string> = {
  ai_generations: "AI Generations",
  scheduled_posts: "Scheduled Posts",
  published_posts: "Published Posts",
  linkedin_connections: "LinkedIn Connections",
  members: "Members",
  workspaces: "Workspaces",
  media_storage: "Media Storage",
};

function buildSettingsDraft(
  preferences: ContentPreference | null,
  voice: VoiceProfile | null,
): SettingsDraft {
  return {
    nicheSlug: preferences?.niche_slug ?? "",
    targetAudience: preferences?.target_audience ?? "",
    contentGoals: (preferences?.content_goals ?? []).join(", "),
    tone: preferences?.tone ?? voice?.summary ?? "",
    language: preferences?.language ?? "en",
    postStyle: preferences?.post_style ?? "",
    ctaPreference: preferences?.cta_preference ?? "",
    hashtagPolicy: preferences?.hashtag_policy ?? "",
    emojiPolicy: preferences?.emoji_policy ?? "",
    topicsToAvoid: (preferences?.topics_to_avoid ?? []).join(", "),
    preferredPostLength: preferences?.preferred_post_length ?? "",
  };
}

function buildVoiceDraft(profile: VoiceProfile | null): VoiceDraft {
  return {
    summary: profile?.summary ?? "",
    traits: (profile?.traits ?? []).join(", "),
    bannedPhrases: (profile?.banned_phrases ?? []).join(", "),
    confidenceScore: String(profile?.confidence_score ?? 0),
  };
}

export default function DashboardClient() {
  const router = useRouter();
  const [view, setView] = useState<DashboardView>("writer");
  const [onboardingOpen, setOnboardingOpen] = useState(true);
  const [step, setStep] = useState(0);
  const [tone, setTone] = useState("Storytelling");
  const [prompt, setPrompt] = useState("");
  const [generated, setGenerated] = useState("");
  const [generatedHashtags, setGeneratedHashtags] = useState<string[]>([...GENERATED_HASHTAGS]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [notification, setNotification] = useState<{ icon: string; message: string } | null>(null);
  const [selectedTags, setSelectedTags] = useState<string[]>([...DEFAULT_SELECTED_TAGS]);
  const [dashboardSnapshot, setDashboardSnapshot] = useState<DashboardSnapshot | null>(null);
  const [dashboardLoadError, setDashboardLoadError] = useState<string | null>(null);
  const [dashboardReloadKey, setDashboardReloadKey] = useState(0);
  const [linkedinConnections, setLinkedinConnections] = useState<LinkedinConnection[]>([]);
  const [selectedConnectionId, setSelectedConnectionId] = useState("");
  const [scheduleDrafts, setScheduleDrafts] = useState<Record<string, string>>({});
  const [contentPreferences, setContentPreferences] = useState<ContentPreference | null>(null);
  const [voiceProfile, setVoiceProfile] = useState<VoiceProfile | null>(null);
  const [writingSamples, setWritingSamples] = useState<WritingSample[]>([]);
  const [nicheProfiles, setNicheProfiles] = useState<NicheProfile[]>([]);
  const [settingsDraft, setSettingsDraft] = useState<SettingsDraft>({
    nicheSlug: "",
    targetAudience: "",
    contentGoals: "",
    tone: "",
    language: "en",
    postStyle: "",
    ctaPreference: "",
    hashtagPolicy: "",
    emojiPolicy: "",
    topicsToAvoid: "",
    preferredPostLength: "",
  });
  const [voiceDraft, setVoiceDraft] = useState<VoiceDraft>({
    summary: "",
    traits: "",
    bannedPhrases: "",
    confidenceScore: "0",
  });
  const [sampleDraft, setSampleDraft] = useState<WritingSampleDraft>({
    title: "",
    body: "",
    source: "",
  });
  const [isSettingsLoading, setIsSettingsLoading] = useState(false);
  const [isSettingsSaving, setIsSettingsSaving] = useState(false);
  const [isIntegrationsLoading, setIsIntegrationsLoading] = useState(false);
  const [isIntegrationsSaving, setIsIntegrationsSaving] = useState(false);
  const notificationTimer = useRef<number | null>(null);
  const generationTimer = useRef<number | null>(null);
  const generationAbortRef = useRef<AbortController | null>(null);

  const currentStep = onboardingSteps[step];

  const showNotif = useCallback((icon: string, message: string) => {
    if (notificationTimer.current) window.clearTimeout(notificationTimer.current);
    setNotification({ icon, message });
    notificationTimer.current = window.setTimeout(() => setNotification(null), 3500);
  }, []);

  const handleLogout = useCallback(async () => {
    try {
      // Sign out from Supabase
      if (supabase) {
        await supabase.auth.signOut();
      }
      // Clear session cookie
      await fetch("/api/auth/session-clear", { method: "POST" });
      // Redirect to login
      router.push("/login");
      router.refresh();
    } catch (error) {
      showNotif("❌", "Failed to sign out. Please try again.");
    }
  }, [router, showNotif]);

  const reloadDashboardSnapshot = useCallback(async (signal?: AbortSignal) => {
    const context = await readDashboardSnapshot(signal);
    setDashboardSnapshot(context);
    setDashboardLoadError(null);
    return context;
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    void (async () => {
      try {
        await reloadDashboardSnapshot(controller.signal);
        if (!active) return;
      } catch (error) {
        if (!active || controller.signal.aborted) return;
        if (error instanceof ApiError && error.status === 401) {
          setDashboardLoadError("Connect the backend session to sync workspace data.");
          showNotif("🔒", "Connect the backend session to sync workspace data.");
          return;
        }
        setDashboardLoadError("Backend workspace sync is unavailable right now.");
        showNotif("⚠️", "Backend workspace sync is unavailable right now.");
      }
    })();

    return () => {
      active = false;
      controller.abort();
      if (notificationTimer.current) window.clearTimeout(notificationTimer.current);
      if (generationTimer.current) window.clearTimeout(generationTimer.current);
      generationAbortRef.current?.abort();
    };
  }, [dashboardReloadKey, reloadDashboardSnapshot, showNotif]);

  useEffect(() => {
    const workspaceId = dashboardSnapshot?.activeWorkspace?.id;
    if (!workspaceId) {
      return;
    }

    const controller = new AbortController();
    let active = true;
    void (async () => {
      setIsSettingsLoading(true);
      try {
        const [preferences, voice, samples, niches] = await Promise.all([
          readContentPreferences(workspaceId, controller.signal),
          readVoiceProfile(workspaceId, controller.signal),
          readWritingSamples(workspaceId, controller.signal),
          readNicheProfiles(controller.signal),
        ]);

        if (!active) return;
        setContentPreferences(preferences);
        setVoiceProfile(voice);
        setWritingSamples(samples.samples);
        setNicheProfiles(niches.niches);
        setSettingsDraft(buildSettingsDraft(preferences, voice));
        setVoiceDraft(buildVoiceDraft(voice));
        setSampleDraft({ title: "", body: "", source: "" });
      } catch (error) {
        if (!active || controller.signal.aborted) return;
        showNotif(
          "⚠️",
          error instanceof Error ? error.message : "Settings data could not be loaded right now.",
        );
      } finally {
        if (active) {
          setIsSettingsLoading(false);
        }
      }
    })();

    return () => {
      active = false;
      controller.abort();
    };
  }, [dashboardSnapshot?.activeWorkspace?.id, showNotif]);

  useEffect(() => {
    const workspaceId = dashboardSnapshot?.activeWorkspace?.id;
    if (!workspaceId) {
      return;
    }

    const controller = new AbortController();
    let active = true;

    void (async () => {
      setIsIntegrationsLoading(true);
      try {
        const result = await readLinkedinConnections(workspaceId, controller.signal);
        if (!active) return;
        setLinkedinConnections(result.connections);
        setSelectedConnectionId((current) => {
          if (result.connections.some((item) => item.id === current)) {
            return current;
          }

          const connected = result.connections.find((item) => item.status === "connected");
          return connected?.id ?? result.connections[0]?.id ?? "";
        });
      } catch (error) {
        if (!active || controller.signal.aborted) return;
        showNotif(
          "⚠️",
          error instanceof Error ? error.message : "LinkedIn connections could not be loaded.",
        );
      } finally {
        if (active) {
          setIsIntegrationsLoading(false);
        }
      }
    })();

    return () => {
      active = false;
      controller.abort();
    };
  }, [dashboardSnapshot?.activeWorkspace?.id, showNotif]);

  function applyPrompt(text: string) {
    setPrompt(text);
    setView("writer");
  }

  function nextStep() {
    if (step < onboardingSteps.length - 1) {
      setStep((value) => value + 1);
      return;
    }

    setOnboardingOpen(false);
    setView("writer");
    showNotif("✦", "Welcome to Qalam! Your Voice Fingerprint is active. Write your first post.");
  }

  function toggleTag(tag: string) {
    setSelectedTags((tags) => (tags.includes(tag) ? tags.filter((item) => item !== tag) : [...tags, tag]));
  }

  function generateContent() {
    if (isGenerating) return;
    if (!prompt.trim()) {
      showNotif("⚠️", "Please describe what you want to write about.");
      return;
    }

    const workspaceId = dashboardSnapshot?.activeWorkspace?.id;
    if (!workspaceId) {
      runLocalGeneration();
      showNotif("✦", "Workspace sync is not ready yet. Generated a local draft instead.");
      return;
    }

    setIsGenerating(true);
    setGenerated("");
    generationAbortRef.current?.abort();
    const controller = new AbortController();
    generationAbortRef.current = controller;

    void (async () => {
      try {
        const result = await generateWorkspacePost(
          workspaceId,
          {
            prompt,
            tone,
            title_internal: "Dashboard draft",
          },
          controller.signal,
        );
        if (controller.signal.aborted) return;
        setGenerated(result.post.body);
        setGeneratedHashtags(result.post.hashtags.length > 0 ? result.post.hashtags : [...GENERATED_HASHTAGS]);
        showNotif(
          "✦",
          `Post generated. Anti-AI score: ${result.quality_score ?? "n/a"}/100`,
        );
      } catch (error) {
        if (controller.signal.aborted) return;
        runLocalGeneration();
        if (error instanceof ApiError) {
          showNotif("⚠️", error.message || "Backend generation failed. Generated a local draft instead.");
          return;
        }
        showNotif("⚠️", "Backend generation failed. Generated a local draft instead.");
      } finally {
        if (generationAbortRef.current === controller) {
          generationAbortRef.current = null;
        }
        setIsGenerating(false);
      }
    })();
  }

  async function copyPost() {
    if (!generated) return;
    try {
      await navigator.clipboard.writeText(generated);
      showNotif("📋", "Post copied to clipboard!");
    } catch {
      showNotif("⚠️", "Clipboard access was blocked by the browser.");
    }
  }

  function runLocalGeneration() {
    setIsGenerating(true);
    setGenerated("");
    if (generationTimer.current) window.clearTimeout(generationTimer.current);
    generationTimer.current = window.setTimeout(() => {
      setGenerated(LOCAL_GENERATED_POST);
      setGeneratedHashtags([...GENERATED_HASHTAGS]);
      setIsGenerating(false);
      showNotif("✦", "Local draft generated. Connect the backend to use live AI output.");
    }, 800);
  }

  function buildMetricCards(items: UsageItem[] | undefined): MetricCard[] {
    if (!items || items.length === 0) {
      return DASHBOARD_METRICS;
    }

    const lookup = new Map(items.map((item) => [item.metric, item]));
    const cards = USAGE_METRIC_ORDER.map((metric) => lookup.get(metric)).filter(
      (item): item is UsageItem => item !== undefined,
    );

    if (cards.length === 0) {
      return DASHBOARD_METRICS;
    }

    return cards.slice(0, 4).map((item) => {
      const label = USAGE_METRIC_LABELS[item.metric] ?? item.metric;
      const value = item.limit ? `${item.used}/${item.limit}` : String(item.used);
      const change = item.limit
        ? `${Math.max(item.limit - item.used, 0)} remaining`
        : "No limit";
      return { label, value, change };
    });
  }

  function buildRecentPosts(posts: DashboardSnapshot["recentPosts"] | undefined): PostSummary[] {
    if (!posts || posts.length === 0) {
      return RECENT_POSTS;
    }

    return posts.map((post) => {
      const metrics = (() => {
        if (post.status === "posted" || post.status === "published") {
          return [post.linkedin_post_urn ? "Published · LinkedIn synced" : "Published"];
        }

        if (post.status === "scheduled") {
          return [
            post.scheduled_for
              ? `Scheduled · ${new Intl.DateTimeFormat("en", {
                  month: "short",
                  day: "numeric",
                  hour: "numeric",
                  minute: "2-digit",
                }).format(new Date(post.scheduled_for))}`
              : "Scheduled",
          ];
        }

        if (post.status === "approved") {
          return ["Approved · Ready to schedule"];
        }

        if (post.status === "publishing") {
          return ["Publishing · LinkedIn queue"];
        }

        if (post.status === "rejected") {
          return [post.rejection_reason ? `Rejected · ${post.rejection_reason}` : "Rejected"];
        }

        if (post.status === "failed") {
          return [post.failure_reason ? `Failed · ${post.failure_reason}` : "Failed"];
        }

        if (post.status === "cancelled") {
          return ["Cancelled"];
        }

        if (post.status === "generated" || post.status === "needs_review") {
          return ["Draft · Needs review"];
        }

        return ["Draft · Needs review"];
      })();

      if (post.hashtags.length > 0) {
        metrics.push(`${post.hashtags.length} hashtags`);
      }

      return {
        id: post.id,
        status: post.status,
        text: post.body,
        metrics,
      };
    });
  }

  function humanizePlanSlug(planSlug: string | undefined | null) {
    if (!planSlug) return "Workspace Plan";
    return planSlug
      .split(/[-_]/)
      .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
      .join(" ");
  }

  function buildPlanDescription(snapshot: DashboardSnapshot | null) {
    const plan = snapshot?.billing?.plan;
    if (plan) {
      const quotas = plan.quotas;
      return `${plan.quotas.monthly_ai_generations} AI generations/mo · ${quotas.monthly_scheduled_posts} scheduled posts/mo · ${quotas.max_members} members`;
    }

    const usage = snapshot?.usage;
    if (usage) {
      const generation = usage.items.find((item) => item.metric === "ai_generations");
      if (generation?.limit) {
        return `${generation.limit} AI generations/mo · ${usage.plan_slug}`;
      }
    }

    return "Backend plan data loading";
  }

  const metricCards = buildMetricCards(dashboardSnapshot?.usage?.items);
  const recentPosts = buildRecentPosts(dashboardSnapshot?.recentPosts);
  const planName = dashboardSnapshot?.billing?.plan?.name ?? humanizePlanSlug(dashboardSnapshot?.usage?.plan_slug);
  const planDescription = buildPlanDescription(dashboardSnapshot);
  const workspaceId = dashboardSnapshot?.activeWorkspace?.id ?? null;
  const billingSummary = dashboardSnapshot?.billing ?? null;

  function saveSettingsPreferences() {
    const workspaceId = dashboardSnapshot?.activeWorkspace?.id;
    if (!workspaceId) return;

    setIsSettingsSaving(true);
    void (async () => {
      try {
        const preferences = await saveContentPreferences(
          workspaceId,
          {
            niche_slug: settingsDraft.nicheSlug || null,
            target_audience: settingsDraft.targetAudience || null,
            content_goals: splitCsv(settingsDraft.contentGoals),
            tone: settingsDraft.tone || null,
            language: settingsDraft.language || "en",
            post_style: settingsDraft.postStyle || null,
            cta_preference: settingsDraft.ctaPreference || null,
            hashtag_policy: settingsDraft.hashtagPolicy || null,
            emoji_policy: settingsDraft.emojiPolicy || null,
            topics_to_avoid: splitCsv(settingsDraft.topicsToAvoid),
            preferred_post_length: settingsDraft.preferredPostLength || null,
          },
        );
        setContentPreferences(preferences);
        showNotif("✦", "Content preferences saved.");
      } catch (error) {
        showNotif("⚠️", error instanceof Error ? error.message : "Failed to save preferences.");
      } finally {
        setIsSettingsSaving(false);
      }
    })();
  }

  function saveSettingsVoiceProfile(payload: VoiceProfileInput) {
    const workspaceId = dashboardSnapshot?.activeWorkspace?.id;
    if (!workspaceId) return;

    setIsSettingsSaving(true);
    void (async () => {
      try {
        const profile = await saveVoiceProfile(workspaceId, payload);
        setVoiceProfile(profile);
        showNotif("🧬", "Voice profile saved.");
      } catch (error) {
        showNotif("⚠️", error instanceof Error ? error.message : "Failed to save voice profile.");
      } finally {
        setIsSettingsSaving(false);
      }
    })();
  }

  function saveSettingsWritingSample() {
    const workspaceId = dashboardSnapshot?.activeWorkspace?.id;
    if (!workspaceId || !sampleDraft.body.trim()) return;

    setIsSettingsSaving(true);
    void (async () => {
      try {
        const sample = await addWritingSample(workspaceId, {
          title: sampleDraft.title.trim() || null,
          body: sampleDraft.body,
          source: sampleDraft.source.trim() || null,
        });
        setWritingSamples((items) => [sample, ...items].slice(0, 3));
        setSampleDraft({ title: "", body: "", source: "" });
        showNotif("✦", "Writing sample saved.");
      } catch (error) {
        showNotif("⚠️", error instanceof Error ? error.message : "Failed to save writing sample.");
      } finally {
        setIsSettingsSaving(false);
      }
    })();
  }

  function splitCsv(value: string) {
    return value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  function updateScheduleDraft(postId: string, value: string) {
    setScheduleDrafts((current) => ({ ...current, [postId]: value }));
  }

  async function connectLinkedIn() {
    if (!workspaceId) {
      showNotif("⚠️", "Workspace data is not ready yet.");
      return;
    }

    try {
      const result = await createLinkedinConnectUrl(workspaceId, {
        redirect_after: window.location.href,
      });
      window.location.assign(result.authorization_url);
    } catch (error) {
      showNotif("⚠️", error instanceof Error ? error.message : "Could not start LinkedIn connect flow.");
    }
  }

  async function disconnectLinkedIn(connectionId: string) {
    if (!workspaceId) return;

    setIsIntegrationsSaving(true);
    try {
      await disconnectLinkedinConnection(workspaceId, connectionId);
      setLinkedinConnections((items) => items.filter((connection) => connection.id !== connectionId));
      if (selectedConnectionId === connectionId) {
        const nextConnection = linkedinConnections.find((item) => item.id !== connectionId);
        setSelectedConnectionId(nextConnection?.id ?? "");
      }
      showNotif("🔗", "LinkedIn connection removed.");
    } catch (error) {
      showNotif("⚠️", error instanceof Error ? error.message : "Failed to disconnect LinkedIn.");
    } finally {
      setIsIntegrationsSaving(false);
    }
  }

  async function publishLinkedInPost(postId: string) {
    if (!workspaceId) return;

    const connectionId =
      linkedinConnections.find((item) => item.id === selectedConnectionId)?.id ??
      linkedinConnections.find((item) => item.status === "connected")?.id ??
      linkedinConnections[0]?.id;

    if (!connectionId) {
      showNotif("⚠️", "Connect LinkedIn before publishing posts.");
      return;
    }

    setIsIntegrationsSaving(true);
    try {
      await publishLinkedinPostNow(workspaceId, postId, connectionId);
      await reloadDashboardSnapshot();
      showNotif("✦", "Post sent to LinkedIn.");
    } catch (error) {
      showNotif("⚠️", error instanceof Error ? error.message : "LinkedIn publish failed.");
    } finally {
      setIsIntegrationsSaving(false);
    }
  }

  async function scheduleLinkedInPost(postId: string) {
    if (!workspaceId) return;

    const value = scheduleDrafts[postId];
    if (!value) {
      showNotif("⚠️", "Choose a schedule time first.");
      return;
    }

    setIsIntegrationsSaving(true);
    try {
      await scheduleWorkspacePost(workspaceId, postId, {
        scheduled_for: new Date(value).toISOString(),
        timezone: dashboardSnapshot?.activeWorkspace?.timezone ?? Intl.DateTimeFormat().resolvedOptions().timeZone,
      });
      await reloadDashboardSnapshot();
      showNotif("📅", "Post scheduled.");
    } catch (error) {
      showNotif("⚠️", error instanceof Error ? error.message : "Failed to schedule post.");
    } finally {
      setIsIntegrationsSaving(false);
    }
  }

  async function cancelLinkedInSchedule(postId: string) {
    if (!workspaceId) return;

    setIsIntegrationsSaving(true);
    try {
      await cancelWorkspacePost(workspaceId, postId);
      await reloadDashboardSnapshot();
      showNotif("↻", "Scheduled post cancelled.");
    } catch (error) {
      showNotif("⚠️", error instanceof Error ? error.message : "Failed to cancel schedule.");
    } finally {
      setIsIntegrationsSaving(false);
    }
  }

  async function startCheckout(planSlug: string) {
    if (!workspaceId) {
      showNotif("⚠️", "Workspace data is not ready yet.");
      return;
    }

    setIsIntegrationsSaving(true);
    try {
      const result = await createCheckoutSession(workspaceId, {
        plan_slug: planSlug,
        success_url: `${window.location.origin}/dashboard?billing=success`,
        cancel_url: `${window.location.origin}/dashboard?billing=cancelled`,
      });
      window.location.assign(result.url);
    } catch (error) {
      showNotif("⚠️", error instanceof Error ? error.message : "Could not create checkout session.");
    } finally {
      setIsIntegrationsSaving(false);
    }
  }

  async function openBillingPortal() {
    if (!workspaceId) {
      showNotif("⚠️", "Workspace data is not ready yet.");
      return;
    }

    setIsIntegrationsSaving(true);
    try {
      const result = await createPortalSession(workspaceId, {
        return_url: `${window.location.origin}/dashboard`,
      });
      window.location.assign(result.url);
    } catch (error) {
      showNotif("⚠️", error instanceof Error ? error.message : "Could not open the billing portal.");
    } finally {
      setIsIntegrationsSaving(false);
    }
  }

  function retryDashboardLoad() {
    setDashboardLoadError(null);
    setDashboardReloadKey((current) => current + 1);
    showNotif("↻", "Retrying workspace sync...");
  }

  return (
    <div className="qalam-dashboard">
      <style>{dashboardStyles}</style>
      <Notification notification={notification} onClose={() => setNotification(null)} />
      {onboardingOpen ? (
        <OnboardingModal
          step={step}
          currentStep={currentStep}
          selectedTags={selectedTags}
          onToggleTag={toggleTag}
          onSkip={() => setOnboardingOpen(false)}
          onNext={nextStep}
        />
      ) : null}

      <div className="shell">
        <Sidebar
          view={view}
          setView={setView}
          showNotif={showNotif}
          planName={planName}
          planDescription={planDescription}
        />
        <main className="main">
          <Topbar view={view} showNotif={showNotif} />
          <div className="content">
            {dashboardLoadError ? (
              <div className="dashboard-banner">
                <div>
                  <div className="dashboard-banner-title">Workspace sync issue</div>
                  <div className="dashboard-banner-sub">{dashboardLoadError}</div>
                </div>
                <button type="button" className="out-btn primary" onClick={retryDashboardLoad}>
                  Retry sync
                </button>
              </div>
            ) : null}
            {view === "landing" ? (
              <div className="landing view-anim active">
                <LandingView setView={setView} openOnboarding={() => setOnboardingOpen(true)} />
              </div>
            ) : null}
            {view === "dashboard" ? (
              <div className="dashboard view-anim active">
                <DashboardOverviewView
                  setView={setView}
                  applyPrompt={applyPrompt}
                  metricCards={metricCards}
                  recentPosts={recentPosts}
                />
              </div>
            ) : null}
            {view === "writer" ? (
              <div className="writer view-anim active">
                <WriterView
                  tone={tone}
                  prompt={prompt}
                  generated={generated}
                  isGenerating={isGenerating}
                  hashtags={generatedHashtags}
                  setTone={setTone}
                  setPrompt={setPrompt}
                  applyPrompt={applyPrompt}
                  generateContent={generateContent}
                  copyPost={copyPost}
                  showNotif={showNotif}
                />
              </div>
            ) : null}
            {view === "voice" ? (
              <div className="voice view-anim active">
                <VoiceView selectedTags={selectedTags} toggleTag={toggleTag} showNotif={showNotif} />
              </div>
            ) : null}
            {view === "analytics" ? (
              <div className="analytics view-anim active">
                <AnalyticsView />
              </div>
            ) : null}
            {view === "integrations" ? (
              <div className="integrations view-anim active">
                <IntegrationsView
                  billingSummary={billingSummary}
                  connections={linkedinConnections}
                  posts={dashboardSnapshot?.recentPosts ?? []}
                  selectedConnectionId={selectedConnectionId}
                  scheduleDrafts={scheduleDrafts}
                  isLoading={isIntegrationsLoading}
                  isSaving={isIntegrationsSaving}
                  onSelectedConnectionIdChange={setSelectedConnectionId}
                  onScheduleDraftChange={updateScheduleDraft}
                  onConnectLinkedIn={connectLinkedIn}
                  onDisconnectLinkedIn={disconnectLinkedIn}
                  onPublishNow={publishLinkedInPost}
                  onSchedulePost={scheduleLinkedInPost}
                  onCancelSchedule={cancelLinkedInSchedule}
                  onUpgradePlan={startCheckout}
                  onOpenBillingPortal={openBillingPortal}
                />
              </div>
            ) : null}
            {view === "settings" ? (
              <div className="settings view-anim active">
                <SettingsView
                  nicheProfiles={nicheProfiles}
                  preferences={contentPreferences}
                  voiceProfile={voiceProfile}
                  writingSamples={writingSamples}
                  settingsDraft={settingsDraft}
                  voiceDraft={voiceDraft}
                  sampleDraft={sampleDraft}
                  isLoading={isSettingsLoading}
                  isSaving={isSettingsSaving}
                  onSettingsDraftChange={(patch) =>
                    setSettingsDraft((current) => ({ ...current, ...patch }))
                  }
                  onVoiceDraftChange={(patch) =>
                    setVoiceDraft((current) => ({ ...current, ...patch }))
                  }
                  onSampleDraftChange={(patch) =>
                    setSampleDraft((current) => ({ ...current, ...patch }))
                  }
                  onSavePreferences={saveSettingsPreferences}
                  onSaveVoiceProfile={saveSettingsVoiceProfile}
                  onSaveWritingSample={saveSettingsWritingSample}
                  onLogout={handleLogout}
                />
              </div>
            ) : null}
          </div>
        </main>
      </div>
    </div>
  );
}
