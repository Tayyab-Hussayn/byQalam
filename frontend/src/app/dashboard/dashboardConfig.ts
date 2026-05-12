import type { DashboardView } from "@/types/dashboard";

export const dashboardTitles: Record<DashboardView, string> = {
  landing: "Qalam",
  dashboard: "Dashboard",
  writer: "AI Writer",
  voice: "Voice Fingerprint",
  analytics: "Analytics",
  integrations: "LinkedIn & Billing",
  settings: "Settings",
};

export const dashboardSubtitles: Record<DashboardView, string> = {
  landing: "Welcome to the future of LinkedIn content",
  dashboard: "Your LinkedIn command center",
  writer: "Your voice, amplified by intelligence",
  voice: "The engine that makes you sound like you",
  analytics: "Performance intelligence for your content",
  integrations: "LinkedIn connection status, publish actions, and plan usage",
  settings: "Workspace preferences, voice profile, and writing samples",
};

export const onboardingSteps = [
  {
    label: "Step 1 of 6",
    title: "Who are you, professionally?",
    sub: "This is how Qalam will introduce your voice to LinkedIn's 1 billion members.",
    progress: 16,
  },
  {
    label: "Step 2 of 6",
    title: "What do you know that others don't?",
    sub: "Your sharpest opinions become your strongest content pillars.",
    progress: 33,
  },
  {
    label: "Step 3 of 6",
    title: "Who are you writing for?",
    sub: "Qalam writes for a specific person, not a vague audience.",
    progress: 50,
  },
  {
    label: "Step 4 of 6",
    title: "Show Qalam your voice.",
    sub: "Paste real posts. The more honest the sample, the better the fingerprint.",
    progress: 66,
  },
  {
    label: "Step 5 of 6",
    title: "Set your LinkedIn goals.",
    sub: "Your goals control what Qalam optimizes for.",
    progress: 83,
  },
  {
    label: "Step 6 of 6",
    title: "Your voice is ready.",
    sub: "Qalam has enough signal to start writing in your style.",
    progress: 100,
  },
] as const;

export const tones = [
  "Storytelling",
  "Bold",
  "Data-Driven",
  "Casual",
  "Professional",
  "Humorous",
] as const;
