import type { MetricCard, PostSummary, QuickAction } from "@/types/dashboard";

export const GENERATED_HASHTAGS = [
  "#hiring",
  "#leadership",
  "#careeradvice",
  "#peopleops",
  "#linkedin",
] as const;

export const DASHBOARD_METRICS: MetricCard[] = [
  { label: "Posts This Month", value: "47", change: "↑ 23% vs last month" },
  { label: "Avg Engagement", value: "6.8%", change: "↑ 2.1x industry avg" },
  { label: "Best Post Score", value: "9.4", change: "↑ Top 5% this week" },
  { label: "Posting Streak", value: "12d", change: "🔥 Personal best!" },
];

export const ANALYTICS_METRICS: MetricCard[] = [
  { label: "Total Impressions", value: "128K", change: "↑ 41% this month" },
  { label: "Engagement Rate", value: "6.8%", change: "2.1x industry average" },
  { label: "Profile Views", value: "3.2K", change: "↑ 89% from posts" },
  { label: "Connection Requests", value: "214", change: "↑ 37 this week" },
];

export const QUICK_ACTIONS: QuickAction[] = [
  {
    icon: "📖",
    label: "Personal Story",
    sublabel: "Hook → Conflict → Lesson",
    prompt: "Write a personal story about a failure that taught me my biggest lesson",
  },
  {
    icon: "⚡",
    label: "Contrarian Take",
    sublabel: "Argue the opposite",
    prompt: "Write a contrarian take on a common belief in my industry",
  },
  {
    icon: "🗓️",
    label: "Weekly Plan",
    sublabel: "7-day content calendar",
    prompt: "Generate my weekly content plan - 5 posts for this week",
  },
  {
    icon: "✨",
    label: "Bio Rewrite",
    sublabel: "SEO + human optimized",
    prompt: "Rewrite my LinkedIn bio and headline for maximum recruiter appeal",
  },
  {
    icon: "🎣",
    label: "Hook Generator",
    sublabel: "10 opening lines",
    prompt: "Generate 10 pattern-interrupt hook lines for my next post",
  },
  {
    icon: "🔄",
    label: "Repurpose",
    sublabel: "1 idea → 3 formats",
    prompt: "Turn this idea into 3 formats: text post, carousel, and poll",
  },
];

export const RECENT_POSTS: PostSummary[] = [
  {
    id: "post_1",
    status: "posted",
    text: "Nobody tells you this when you start in HR: the hardest part isn't firing people. It's the moment before. When you know what's coming and they don't...",
    metrics: ["👁 4,280", "❤️ 312", "💬 89", "Score: 9.4"],
  },
  {
    id: "post_2",
    status: "scheduled",
    text: "Three years ago I was rejected from 47 jobs in a row. Today I run the hiring for a 200-person company. Here's exactly what changed...",
    metrics: ["Scheduled · Tomorrow 9:00 AM"],
  },
  {
    id: "post_3",
    status: "draft",
    text: "The interview question that reveals everything about a candidate's emotional intelligence (and almost nobody asks it)...",
    metrics: ["Draft · Edit before posting"],
  },
];

export const STREAK_HEAT = [
  1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1,
  1, 1, 1, 0, 0, 1, 1, 1, 1, 0,
] as const;

export const HEAT_LEVELS = [
  0, 1, 2, 3, 2, 1, 0, 1, 3, 2, 1, 0, 2, 3, 1, 2, 3, 0, 1, 2, 3, 2, 1, 0, 1,
  2, 3, 1, 0, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1, 2, 3,
  2, 1, 0, 2, 3, 1,
] as const;
