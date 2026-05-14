import {
  ANALYTICS_METRICS,
  DASHBOARD_METRICS,
  HEAT_LEVELS,
  QUICK_ACTIONS,
  RECENT_POSTS,
  STREAK_HEAT,
} from "@/features/dashboard/data/dashboardMock";
import type { DashboardView, MetricCard, PostSummary, PostStatus } from "@/types/dashboard";
import type {
  ContentPreference,
  NicheProfile,
  VoiceProfile,
  VoiceProfileInput,
  WritingSample,
} from "@/services/preferences";
import type { BillingSummary } from "@/services/billing";
import type { LinkedinConnection, LinkedinConnectionStatus } from "@/services/linkedin";
import type { PostRecord } from "@/services/posts";
import { tones } from "../dashboardConfig";
import { SparkIcon } from "./DashboardIcons";

export function LandingView({ setView, openOnboarding }: { setView: (view: DashboardView) => void; openOnboarding: () => void }) {
  return (
    <>
      <div className="hero">
        <div className="hero-badge"><span className="hero-badge-dot" />Now live - 1,240 professionals writing with Qalam</div>
        <h1 className="serif">The pen that<br /><em>never runs dry</em></h1>
        <p>Qalam learns your voice so deeply that your audience, LinkedIn&apos;s algorithm, and even you can&apos;t tell it was AI-written. The first voice-native content engine built for the global professional.</p>
        <div className="hero-cta">
          <button className="btn-primary" type="button" onClick={openOnboarding}>Start Writing Free →</button>
          <button className="btn-ghost" type="button" onClick={() => setView("writer")}>See it in action</button>
        </div>
      </div>
      <div className="features-grid">
        <button className="feat-card" type="button" onClick={() => setView("voice")}><div className="feat-icon">🧬</div><h3>Voice Fingerprint Engine</h3><p>200+ parameters capture how you write - sentence rhythm, emoji use, humor style, vocabulary level - refined with every post.</p></button>
        <button className="feat-card" type="button" onClick={() => setView("writer")}><div className="feat-icon">✦</div><h3>Zero AI Slop Guarantee</h3><p>A 200+ banned-phrase filter tuned to LinkedIn&apos;s authenticity signals. No &quot;thrilled to share.&quot; No &quot;game-changer.&quot; Just you.</p></button>
        <button className="feat-card" type="button" onClick={() => setView("analytics")}><div className="feat-icon">📈</div><h3>Performance Intelligence</h3><p>Every post feeds back into your Voice Fingerprint. Qalam learns what makes your audience stop scrolling - and does more of it.</p></button>
      </div>
    </>
  );
}

export function DashboardView({
  setView,
  applyPrompt,
  metricCards = DASHBOARD_METRICS,
  recentPosts = RECENT_POSTS,
}: {
  setView: (view: DashboardView) => void;
  applyPrompt: (prompt: string) => void;
  metricCards?: MetricCard[];
  recentPosts?: PostSummary[];
}) {
  return (
    <>
      <div className="stats-row">
        {metricCards.map(({ label, value, change }) => <div className="stat-card" key={label}><div className="stat-label">{label}</div><div className="stat-val shimmer">{value}</div><div className="stat-change">{change}</div></div>)}
      </div>
      <div className="dash-grid">
        <div>
          <div className="quick-actions">
            <div className="section-title serif">Quick Actions</div>
            <div className="qa-grid">
              {QUICK_ACTIONS.map((action) => <button key={action.label} className="qa-btn" type="button" onClick={() => applyPrompt(action.prompt)}><div className="qa-btn-icon">{action.icon}</div><span className="qa-btn-label">{action.label}</span><div className="qa-btn-sub">{action.sublabel}</div></button>)}
            </div>
          </div>
          <RecentPosts posts={recentPosts} />
        </div>
        <div>
          <StreakCard />
          <div className="voice-card" style={{ marginTop: 16 }}>
            <div className="section-title serif">Voice Health</div>
            <VoiceMeters rows={[["Authenticity", 92], ["Engagement", 78], ["Consistency", 85], ["AI Detection", 96]]} />
            <button className="out-btn" style={{ width: "100%", justifyContent: "center", marginTop: 4 }} type="button" onClick={() => setView("voice")}>Refine Voice Fingerprint →</button>
          </div>
        </div>
      </div>
    </>
  );
}

function RecentPosts({ posts }: { posts: PostSummary[] }) {
  return (
    <div className="recent-posts" style={{ marginTop: 20 }}>
      <div className="section-title serif">Recent Posts</div>
      {posts.map((post) => <PostItem key={post.id} status={post.status} text={post.text} meta={post.metrics} />)}
    </div>
  );
}

function PostItem({ status, text, meta }: { status: PostStatus; text: string; meta: string[] }) {
  const statusClass = getPostStatusClass(status);

  return (
    <div className="post-item">
      <div className={`post-status ${statusClass}`} />
      <div className="post-content">
        <div className="post-text">{text}</div>
        <div className="post-meta">{meta.map((item) => <span className="post-metric" key={item}>{item}</span>)}</div>
      </div>
    </div>
  );
}

function getPostStatusClass(status: PostStatus) {
  if (status === "posted" || status === "published") {
    return "posted";
  }
  if (status === "scheduled" || status === "approved" || status === "publishing") {
    return "sched";
  }
  return "draft";
}

function getPostStatusLabel(status: PostStatus) {
  if (status === "posted" || status === "published") return "Published";
  if (status === "scheduled") return "Scheduled";
  if (status === "approved") return "Approved";
  if (status === "publishing") return "Publishing";
  if (status === "generated") return "Generated";
  if (status === "needs_review") return "Needs review";
  if (status === "rejected") return "Rejected";
  if (status === "failed") return "Failed";
  if (status === "cancelled") return "Cancelled";
  return "Draft";
}

function getConnectionStatusLabel(status: LinkedinConnectionStatus) {
  if (status === "connected") return "Connected";
  if (status === "expired") return "Expired";
  if (status === "revoked") return "Revoked";
  if (status === "failed" || status === "error") return "Needs attention";
  return status;
}

function getConnectionStatusClass(status: LinkedinConnectionStatus) {
  if (status === "connected") return "connected";
  if (status === "expired" || status === "revoked" || status === "failed" || status === "error") {
    return "expired";
  }
  return "connected";
}

function getSubscriptionStatusLabel(status: string | null | undefined) {
  if (!status) return "Unsubscribed";
  return status
    .split(/[_-]/)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

function humanizePlanSlug(planSlug: string | undefined | null) {
  if (!planSlug) return "Workspace Plan";
  return planSlug
    .split(/[-_]/)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

function getUpgradePlans(currentSlug: string | undefined | null) {
  const planOrder = ["free", "starter", "pro", "agency"] as const;
  const currentIndex = currentSlug ? planOrder.indexOf(currentSlug as (typeof planOrder)[number]) : 0;
  return planOrder.slice(Math.max(currentIndex + 1, 1));
}

function formatDateTime(value: string | null | undefined) {
  if (!value) return "Not scheduled";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function toDatetimeLocalValue(value: string | null | undefined) {
  if (!value) return "";
  const date = new Date(value);
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60000);
  return local.toISOString().slice(0, 16);
}

function getUsagePercent(used: number, limit: number | null) {
  if (!limit || limit <= 0) return 0;
  return Math.min(100, Math.round((used / limit) * 100));
}

function StreakCard() {
  return (
    <div className="streak-card">
      <div className="section-title serif">Posting Streak</div>
      <p style={{ fontSize: 12, color: "var(--text3)", marginBottom: 8 }}>May 2026</p>
      <div className="streak-dots">
        {["M", "T", "W", "T", "F", "S", "S"].map((day, index) => <div key={`${day}-${index}`} style={{ fontSize: 9, color: "var(--text3)", textAlign: "center", width: 28 }}>{day}</div>)}
        {STREAK_HEAT.map((heat, index) => <div key={index} className={`s-dot ${index === STREAK_HEAT.length - 1 ? "today" : heat ? "done" : "miss"}`}>{index === STREAK_HEAT.length - 1 ? "★" : heat ? "✓" : ""}</div>)}
      </div>
      <p style={{ fontSize: 12, color: "var(--text2)", marginTop: 8 }}>🔥 12-day streak. Your audience expects you now. Don&apos;t break it.</p>
    </div>
  );
}

export function WriterView({
  tone,
  prompt,
  generated,
  isGenerating,
  hashtags,
  setTone,
  setPrompt,
  applyPrompt,
  generateContent,
  copyPost,
  showNotif,
}: {
  tone: string;
  prompt: string;
  generated: string;
  isGenerating: boolean;
  hashtags: string[];
  setTone: (tone: string) => void;
  setPrompt: (prompt: string) => void;
  applyPrompt: (prompt: string) => void;
  generateContent: () => void;
  copyPost: () => void;
  showNotif: (icon: string, message: string) => void;
}) {
  return (
    <div className="writer-layout">
      <div>
        <div className="writer-panel">
          <div className="panel-header"><span className="panel-title">Voice + Tone</span><span style={{ fontSize: 11, color: "var(--gold)" }}>🧬 Voice Fingerprint Active</span></div>
          <div className="tone-pills">{tones.map((item) => <button key={item} type="button" className={`tone-pill ${tone === item ? "active" : ""}`} onClick={() => setTone(item)}>{item}</button>)}</div>
          <div className="prompt-area">
            <div className="prompt-label">What do you want to write about?</div>
            <textarea className="prompt-input" rows={5} value={prompt} onChange={(event) => setPrompt(event.target.value)} placeholder={"e.g. The time I failed publicly and what it taught me about leadership...\n\nOr just a topic: rejection in job hunting, AI in HR, building in public...\n\nQalam knows your voice - just give it a direction."} />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 8 }}>
              <select className="field-input" style={{ fontSize: 13, cursor: "pointer" }}><option>LinkedIn Post</option><option>10 Hooks</option><option>Carousel Script</option><option>Weekly Plan</option><option>Bio Rewrite</option><option>Comment Replies</option></select>
              <select className="field-input" style={{ fontSize: 13, cursor: "pointer" }}><option>Medium (600-900 chars)</option><option>Short (under 400)</option><option>Long (1200+)</option><option>Viral format</option></select>
            </div>
            <button className="generate-btn" type="button" disabled={isGenerating} onClick={generateContent}>{isGenerating ? <span className="typing-cursor" /> : <SparkIcon />}{isGenerating ? "Qalam is writing..." : "Generate with Qalam"}</button>
          </div>
        </div>
        <div style={{ marginTop: 12, display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 8 }}>
          <button className="qa-btn" type="button" onClick={() => applyPrompt("Write about a failure that became my greatest professional lesson")}><span className="qa-btn-label" style={{ fontSize: 12 }}>💡 Story Prompt</span></button>
          <button className="qa-btn" type="button" onClick={() => applyPrompt("Share a contrarian view on hiring that most recruiters get wrong")}><span className="qa-btn-label" style={{ fontSize: 12 }}>⚡ Contrarian</span></button>
          <button className="qa-btn" type="button" onClick={() => applyPrompt("Share 3 things I wish I knew before leading my first team")}><span className="qa-btn-label" style={{ fontSize: 12 }}>📋 List Post</span></button>
        </div>
      </div>
      <div className="output-panel">
        <div className="panel-header"><span className="panel-title">Generated Post</span><span style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-jetbrains-mono),monospace" }}>claude-sonnet-4-6</span></div>
        <div className="output-content">
          {!generated && !isGenerating ? <OutputPlaceholder /> : <div className="generated-post">{generated || <span className="typing-cursor" />}</div>}
        </div>
        {generated ? (
          <>
            <div className="output-actions">
              <button className="out-btn" type="button" onClick={copyPost}>📋 Copy</button>
              <button className="out-btn" type="button" onClick={generateContent}>↻ Regenerate</button>
              <button className="out-btn" type="button" onClick={() => showNotif("📅", "Post saved to Content Calendar for tomorrow 9:00 AM")}>📅 Schedule</button>
              <button className="out-btn primary" type="button" onClick={() => showNotif("✦", "Post saved to your Content Library!")}>Save Draft</button>
            </div>
            <div style={{ padding: "0 20px 16px" }}><div style={{ fontSize: 11, color: "var(--text3)", marginBottom: 6, letterSpacing: "0.08em", textTransform: "uppercase" }}>Suggested Hashtags</div><div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>{hashtags.map((tag) => <button key={tag} type="button" style={{ background: "var(--glass)", border: "1px solid var(--border)", borderRadius: 20, padding: "3px 10px", fontSize: 11, color: "var(--gold-light)", cursor: "pointer" }} onClick={() => showNotif("📋", `${tag} copied!`)}>{tag}</button>)}</div></div>
            <div style={{ padding: "0 20px 16px", borderTop: "1px solid var(--border)" }}><div style={{ fontSize: 11, color: "var(--text3)", marginBottom: 6, letterSpacing: "0.08em", textTransform: "uppercase" }}>First Comment (links go here)</div><div style={{ fontSize: 13, color: "var(--text2)", lineHeight: 1.6 }}>Drop any questions in the comments - I read every single one.</div></div>
          </>
        ) : null}
      </div>
    </div>
  );
}

function OutputPlaceholder() {
  return (
    <div className="output-placeholder">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="1.5">
        <circle cx="24" cy="22" r="16" strokeDasharray="4 3" />
        <path d="M24 10 C24 10,18 18,18 22 C18 25.3 20.7 28 24 28 C27.3 28 30 25.3 30 22 C30 18 24 10 24 10Z" fill="currentColor" opacity="0.3" />
        <path d="M16 38 Q22 34 26 37 Q30 40 34 37" strokeLinecap="round" />
      </svg>
      <p>Your post will appear here.<br />Write something. Qalam will<br />make it sound like <em>you</em>.</p>
    </div>
  );
}

export function VoiceView({ selectedTags, toggleTag, showNotif }: { selectedTags: string[]; toggleTag: (tag: string) => void; showNotif: (icon: string, message: string) => void }) {
  const banned = ["thrilled to share", "game-changing", "paradigm shift", "delve into", "passionate about", "thought leader", "leveraging", "synergy", "+ Add phrase"];
  return (
    <>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 20, marginBottom: 20 }}>
        <div className="voice-card">
          <div className="section-title serif">Voice Fingerprint</div>
          <p style={{ fontSize: 12, color: "var(--text3)", marginBottom: 8 }}>Auto-extracted from your writing. Refined with every generation.</p>
          <div className="fp-visual"><span className="fp-key">&quot;avg_sentence_length&quot;</span>: <span className="fp-val">11</span>,<br /><span className="fp-key">&quot;vocabulary&quot;</span>: <span className="fp-val">&quot;conversational&quot;</span>,<br /><span className="fp-key">&quot;emoji_frequency&quot;</span>: <span className="fp-val">&quot;rare&quot;</span>,<br /><span className="fp-key">&quot;uses_questions&quot;</span>: <span className="fp-val">true</span>,<br /><span className="fp-key">&quot;humor_style&quot;</span>: <span className="fp-val">&quot;dry&quot;</span>,<br /><span className="fp-key">&quot;formality&quot;</span>: <span className="fp-val">0.38</span>,<br /><span className="fp-key">&quot;opens_with&quot;</span>: <span className="fp-val">&quot;bold_statement&quot;</span>,<br /><span className="fp-key">&quot;closes_with&quot;</span>: <span className="fp-val">&quot;question&quot;</span>,<br /><span className="fp-key">&quot;line_break&quot;</span>: <span className="fp-val">&quot;one_idea_per_line&quot;</span>,<br /><span className="fp-key">&quot;signature&quot;</span>: <span className="fp-val">[&quot;Here is what I know&quot;,&quot;Three things:&quot;]</span></div>
          <button className="out-btn" style={{ width: "100%", marginTop: 4 }} type="button" onClick={() => showNotif("🧬", "Re-analyzing your 47 posts to refine voice fingerprint...")}>Re-analyze Voice →</button>
        </div>
        <div className="voice-card">
          <div className="section-title serif">Writing Samples</div>
          <p style={{ fontSize: 12, color: "var(--text3)", marginBottom: 8 }}>Paste 3 real LinkedIn posts you wrote. The more authentic, the better.</p>
          <div className="sample-box"><textarea rows={4} placeholder={"Paste your best LinkedIn post here...\n\nThe one that got the most comments. The one where people said 'this is SO you.'"} /></div>
          <div className="sample-box" style={{ marginTop: 8 }}><textarea rows={3} placeholder="Another post - different topic, same voice..." /></div>
          <button className="out-btn" style={{ width: "100%", marginTop: 10 }} type="button" onClick={() => showNotif("✦", "Voice samples saved. Re-training fingerprint model...")}>Save Samples →</button>
        </div>
        <div className="voice-card">
          <div className="section-title serif">Voice Metrics</div>
          <VoiceMeters rows={[["Authenticity", 92], ["Consistency", 85], ["Readability", 88], ["Hook Strength", 79], ["Anti-AI Score", 96], ["Engagement", 78]]} />
          <div style={{ background: "var(--surface3)", border: "1px solid var(--border)", borderRadius: "var(--r8)", padding: 12, marginTop: 8 }}><div style={{ fontSize: 11, color: "var(--gold)", marginBottom: 4 }}>AI says:</div><div style={{ fontSize: 12, color: "var(--text2)", lineHeight: 1.6 }}>Your anti-AI score is elite. Your hook strength can improve - try opening with a number or a counter-intuitive statement instead of a question.</div></div>
        </div>
      </div>
      <div className="voice-card">
        <div className="section-title serif">Persona Configuration</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16 }}>
          <div className="field-group"><div className="field-label">Target Audience</div><input className="field-input" placeholder="HR managers, startup founders..." defaultValue="HR managers & job seekers" /></div>
          <div className="field-group"><div className="field-label">Primary Goal</div><select className="field-input" defaultValue="Thought Leadership"><option>Brand Building</option><option>Lead Generation</option><option>Thought Leadership</option><option>Job Offers</option></select></div>
          <div className="field-group"><div className="field-label">Unique Perspective</div><input className="field-input" placeholder="What makes YOUR view different?" defaultValue="Hiring is broken - and I have the data" /></div>
          <div className="field-group"><div className="field-label">Posting Frequency</div><select className="field-input" defaultValue="5x / week"><option>Daily</option><option>5x / week</option><option>3x / week</option><option>Weekly</option></select></div>
        </div>
        <div style={{ marginTop: 16 }}><div className="field-label">Banned Phrases (your personal blocklist)</div><div className="tag-select">{banned.map((tag) => <button type="button" key={tag} className={`tag ${selectedTags.includes(tag) ? "selected" : ""}`} onClick={() => toggleTag(tag)}>{tag}</button>)}</div></div>
        <button className="generate-btn" style={{ marginTop: 16, maxWidth: 260 }} type="button" onClick={() => showNotif("🧬", "Voice Fingerprint updated and saved. Future posts will reflect your new preferences.")}>Save Voice Profile →</button>
      </div>
    </>
  );
}

function VoiceMeters({ rows }: { rows: [string, number][] }) {
  return (
    <div className="voice-meter">
      {rows.map(([label, value]) => <div className="meter-row" key={label}><div className="meter-label">{label}</div><div className="meter-track"><div className="meter-fill" style={{ width: `${value}%` }} /></div><div className="meter-val" style={label.includes("AI") ? { color: "#4CAF50" } : undefined}>{value}</div></div>)}
    </div>
  );
}

export function AnalyticsView() {
  return (
    <>
      <div className="stats-row">{ANALYTICS_METRICS.map(({ label, value, change }) => <div className="stat-card" key={label}><div className="stat-label">{label}</div><div className="stat-val shimmer">{value}</div><div className="stat-change">{change}</div></div>)}</div>
      <div className="analytics-grid">
        <div className="chart-card"><div className="section-title serif">Engagement by Day</div><div className="chart-bars">{["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day, index) => <div className="bar-wrap" key={day}><div className="bar" style={{ height: `${[42, 88, 56, 95, 73, 38, 61][index]}%` }} /><div className="bar-label">{day}</div></div>)}</div></div>
        <div className="chart-card"><div className="section-title serif">Content Mix</div><div className="donut-wrap"><Donut /><div className="donut-legend">{[["var(--gold)", "Personal Stories", "40%"], ["var(--teal)", "Thought Leadership", "24%"], ["var(--teal-light)", "Engagement Posts", "16%"], ["var(--border2)", "Other Formats", "20%"]].map(([color, label, pct]) => <div className="legend-item" key={label}><div className="legend-dot" style={{ background: color }} /><span className="legend-text">{label}</span><span className="legend-pct">{pct}</span></div>)}</div></div></div>
        <div className="chart-card" style={{ gridColumn: "span 2" }}><div className="section-title serif">Posting Heatmap - Last 8 Weeks</div><div className="heatmap">{HEAT_LEVELS.slice(0, 56).map((level, index) => <div className={`heat-cell heat-${level}`} title={`Engagement level ${level}`} key={index} />)}</div><div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 10, fontSize: 11, color: "var(--text3)" }}><span>Less</span><div style={{ width: 12, height: 12, borderRadius: 3, background: "var(--surface3)" }} /><div style={{ width: 12, height: 12, borderRadius: 3, background: "rgba(13,92,74,0.4)" }} /><div style={{ width: 12, height: 12, borderRadius: 3, background: "var(--teal)" }} /><div style={{ width: 12, height: 12, borderRadius: 3, background: "var(--gold-dim)" }} /><span>More engagement</span></div></div>
      </div>
    </>
  );
}

export function IntegrationsView({
  billingSummary,
  connections,
  posts,
  selectedConnectionId,
  scheduleDrafts,
  isLoading,
  isSaving,
  onSelectedConnectionIdChange,
  onScheduleDraftChange,
  onConnectLinkedIn,
  onDisconnectLinkedIn,
  onPublishNow,
  onSchedulePost,
  onCancelSchedule,
  onUpgradePlan,
  onOpenBillingPortal,
}: {
  billingSummary: BillingSummary | null;
  connections: LinkedinConnection[];
  posts: PostRecord[];
  selectedConnectionId: string;
  scheduleDrafts: Record<string, string>;
  isLoading: boolean;
  isSaving: boolean;
  onSelectedConnectionIdChange: (connectionId: string) => void;
  onScheduleDraftChange: (postId: string, value: string) => void;
  onConnectLinkedIn: () => void;
  onDisconnectLinkedIn: (connectionId: string) => void;
  onPublishNow: (postId: string) => void;
  onSchedulePost: (postId: string) => void;
  onCancelSchedule: (postId: string) => void;
  onUpgradePlan: (planSlug: string) => void;
  onOpenBillingPortal: () => void;
}) {
  const planSlug = billingSummary?.plan?.slug ?? billingSummary?.usage.plan_slug ?? null;
  const upgradePlans = getUpgradePlans(planSlug);
  const selectedConnection =
    connections.find((item) => item.id === selectedConnectionId) ??
    connections.find((item) => item.status === "connected") ??
    connections[0] ??
    null;
  const connectedCount = connections.filter((item) => item.status === "connected").length;
  const actionablePosts = posts.filter((item) =>
    ["approved", "scheduled", "published", "posted"].includes(item.status),
  );

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div className="integrations-grid">
        <div className="voice-card account-card">
          <div className="section-title serif">LinkedIn Connections</div>
          <p style={{ fontSize: 12, color: "var(--text3)", marginBottom: 14, lineHeight: 1.6 }}>
            Connect a personal profile or company page, keep an eye on token status, and disconnect
            safely when a workspace no longer needs access.
          </p>
          <div className="account-meta-row">
            <span className="status-pill">{connectedCount} connected</span>
            <span className="account-muted">{connections.length} total connection{connections.length === 1 ? "" : "s"}</span>
          </div>
          <button className="generate-btn" type="button" disabled={isLoading || isSaving} onClick={onConnectLinkedIn}>
            {isLoading ? "Loading LinkedIn..." : "Connect LinkedIn"}
          </button>
          <div className="connection-list">
            {connections.length > 0 ? (
              connections.map((connection) => (
                <div key={connection.id} className="connection-row">
                  <div className="connection-main">
                    <div className="connection-title">
                      {connection.display_name ?? connection.target_urn}
                    </div>
                    <div className="connection-sub">
                      {connection.target_type} · {connection.target_urn}
                    </div>
                    <div className="connection-sub">
                      Expires {connection.token_expires_at ? formatDateTime(connection.token_expires_at) : "never"}
                    </div>
                    <div className="tag-select" style={{ marginTop: 10 }}>
                      {connection.scopes.map((scope) => (
                        <span key={scope} className="tag selected" style={{ cursor: "default" }}>
                          {scope}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="connection-side">
                    <span className={`status-pill ${getConnectionStatusClass(connection.status)}`}>
                      {getConnectionStatusLabel(connection.status)}
                    </span>
                    <button
                      type="button"
                      className="out-btn"
                      disabled={isSaving}
                      onClick={() => onSelectedConnectionIdChange(connection.id)}
                    >
                      Use for publishing
                    </button>
                    <button
                      type="button"
                      className="out-btn"
                      disabled={isSaving}
                      onClick={() => onDisconnectLinkedIn(connection.id)}
                    >
                      Disconnect
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="account-empty">
                No LinkedIn connection yet. Connect a profile to enable publishing.
              </div>
            )}
          </div>
          {selectedConnection ? (
            <div className="account-note">
              Publishing target: {selectedConnection.display_name ?? selectedConnection.target_urn}
            </div>
          ) : null}
        </div>

        <div className="voice-card account-card">
          <div className="section-title serif">Billing & Quotas</div>
          <p style={{ fontSize: 12, color: "var(--text3)", marginBottom: 14, lineHeight: 1.6 }}>
            Track the active plan, subscription state, and workspace limits from the backend. Upgrade
            buttons use the real Stripe session flow.
          </p>
          <div className="billing-header">
            <div>
              <div className="billing-plan">{billingSummary?.plan?.name ?? humanizePlanSlug(planSlug)}</div>
              <div className="billing-sub">
                {getSubscriptionStatusLabel(billingSummary?.subscription?.status)} · {billingSummary?.subscription?.cancel_at_period_end ? "Cancels at period end" : "Auto-renews"}
              </div>
            </div>
            <button className="out-btn" type="button" disabled={isSaving} onClick={onOpenBillingPortal}>
              Open billing portal
            </button>
          </div>
          <div className="billing-period">
            Period ends {billingSummary?.subscription?.current_period_end ? formatDateTime(billingSummary.subscription.current_period_end) : "when the current cycle ends"}
          </div>

          <div className="quota-list">
            {(billingSummary?.usage.items ?? []).map((item) => (
              <div key={item.metric} className="quota-row">
                <div className="quota-head">
                  <span className="quota-label">{item.metric.replace(/_/g, " ")}</span>
                  <span className="quota-value">
                    {item.used}
                    {item.limit ? ` / ${item.limit}` : ""}
                  </span>
                </div>
                <div className="quota-track">
                  <div className="quota-fill" style={{ width: `${getUsagePercent(item.used, item.limit)}%` }} />
                </div>
              </div>
            ))}
          </div>

          <div className="plan-option-grid">
            {upgradePlans.length > 0 ? (
              upgradePlans.map((slug) => (
                <button
                  key={slug}
                  className="plan-option"
                  type="button"
                  disabled={isSaving}
                  onClick={() => onUpgradePlan(slug)}
                >
                  <div className="plan-option-title">{humanizePlanSlug(slug)}</div>
                  <div className="plan-option-sub">Upgrade through Stripe checkout</div>
                </button>
              ))
            ) : (
              <div className="account-empty">You are already on the highest plan.</div>
            )}
          </div>
        </div>
      </div>

      <div className="voice-card account-card">
        <div className="section-title serif">Publishing Queue</div>
        <p style={{ fontSize: 12, color: "var(--text3)", marginBottom: 14, lineHeight: 1.6 }}>
          Approved posts can be scheduled here. Scheduled posts can be published immediately from the
          same workspace with a connected LinkedIn account.
        </p>
        <div className="publishing-toolbar">
          <div className="field-group" style={{ marginBottom: 0 }}>
            <div className="field-label">Publishing connection</div>
            <select
              className="field-input"
              value={selectedConnectionId}
              onChange={(event) => onSelectedConnectionIdChange(event.target.value)}
            >
              <option value="">Select a LinkedIn connection</option>
              {connections.map((connection) => (
                <option key={connection.id} value={connection.id}>
                  {connection.display_name ?? connection.target_urn}
                </option>
              ))}
            </select>
          </div>
          <div className="account-muted">
            {selectedConnection ? `Using ${selectedConnection.display_name ?? selectedConnection.target_urn}` : "Select a connection to publish now."}
          </div>
        </div>

        <div className="publishing-list">
          {actionablePosts.length > 0 ? (
            actionablePosts.map((post) => {
              const scheduleValue = scheduleDrafts[post.id] ?? toDatetimeLocalValue(post.scheduled_for);
              const canSchedule = post.status === "approved";
              const canPublish = post.status === "approved" || post.status === "scheduled";
              const canCancel = post.status === "scheduled";

              return (
                <div key={post.id} className="publish-row">
                  <div className="publish-main">
                    <div className="publish-status-row">
                      <span className={`status-pill ${getPostStatusClass(post.status)}`}>
                        {getPostStatusLabel(post.status)}
                      </span>
                      <span className="account-muted">{post.linkedin_post_urn ? "Synced to LinkedIn" : post.failure_reason ? "Needs attention" : "Workspace post"}</span>
                    </div>
                    <div className="publish-text">{post.body}</div>
                    <div className="account-muted">
                      {post.scheduled_for ? `Scheduled for ${formatDateTime(post.scheduled_for)}` : "No scheduled time yet."}
                    </div>
                  </div>

                  <div className="publish-side">
                    {canSchedule ? (
                      <div className="field-group" style={{ marginBottom: 0 }}>
                        <div className="field-label">Schedule for</div>
                        <input
                          className="field-input"
                          type="datetime-local"
                          value={scheduleValue}
                          onChange={(event) => onScheduleDraftChange(post.id, event.target.value)}
                        />
                      </div>
                    ) : null}

                    <div className="publish-actions">
                      <button
                        type="button"
                        className="out-btn primary"
                        disabled={isSaving || !selectedConnection || !canPublish}
                        onClick={() => onPublishNow(post.id)}
                      >
                        Publish now
                      </button>
                      {canSchedule ? (
                        <button
                          type="button"
                          className="out-btn"
                          disabled={isSaving || !scheduleValue}
                          onClick={() => onSchedulePost(post.id)}
                        >
                          Schedule
                        </button>
                      ) : null}
                      {canCancel ? (
                        <button
                          type="button"
                          className="out-btn"
                          disabled={isSaving}
                          onClick={() => onCancelSchedule(post.id)}
                        >
                          Cancel schedule
                        </button>
                      ) : null}
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="account-empty">
              No approved or scheduled posts are ready for LinkedIn publishing yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function SettingsView({
  nicheProfiles,
  preferences,
  voiceProfile,
  writingSamples,
  settingsDraft,
  voiceDraft,
  sampleDraft,
  isLoading,
  isSaving,
  onSettingsDraftChange,
  onVoiceDraftChange,
  onSampleDraftChange,
  onSavePreferences,
  onSaveVoiceProfile,
  onSaveWritingSample,
  onLogout,
}: {
  preferences: ContentPreference | null;
  voiceProfile: VoiceProfile | null;
  writingSamples: WritingSample[];
  nicheProfiles: NicheProfile[];
  settingsDraft: SettingsDraft;
  voiceDraft: VoiceDraft;
  sampleDraft: WritingSampleDraft;
  isLoading: boolean;
  isSaving: boolean;
  onSettingsDraftChange: (patch: Partial<SettingsDraft>) => void;
  onVoiceDraftChange: (patch: Partial<VoiceDraft>) => void;
  onSampleDraftChange: (patch: Partial<WritingSampleDraft>) => void;
  onSavePreferences: () => void;
  onSaveVoiceProfile: (payload: VoiceProfileInput) => void;
  onSaveWritingSample: () => void;
  onLogout: () => void;
}) {
  const selectedNiche = nicheProfiles.find((item) => item.slug === settingsDraft.nicheSlug) ?? nicheProfiles[0] ?? null;

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div className="voice-card">
        <div className="section-title serif">Content Preferences</div>
        {preferences ? (
          <div style={{ fontSize: 12, color: "var(--text3)", marginBottom: 12 }}>
            Saved profile loaded for {preferences.language.toUpperCase()}.
          </div>
        ) : null}
        <div className="field-row">
          <div className="field-group">
            <div className="field-label">Niche</div>
            <select
              className="field-input"
              value={settingsDraft.nicheSlug}
              onChange={(event) => onSettingsDraftChange({ nicheSlug: event.target.value })}
            >
              <option value="">Select a niche</option>
              {nicheProfiles.map((niche) => (
                <option key={niche.id} value={niche.slug}>
                  {niche.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field-group">
            <div className="field-label">Tone</div>
            <input
              className="field-input"
              value={settingsDraft.tone}
              onChange={(event) => onSettingsDraftChange({ tone: event.target.value })}
              placeholder="Professional, bold, conversational..."
            />
          </div>
        </div>
        <div className="field-group">
          <div className="field-label">Target Audience</div>
          <input
            className="field-input"
            value={settingsDraft.targetAudience}
            onChange={(event) => onSettingsDraftChange({ targetAudience: event.target.value })}
            placeholder="Who should your posts speak to?"
          />
        </div>
        <div className="field-row">
          <div className="field-group">
            <div className="field-label">Post Style</div>
            <input
              className="field-input"
              value={settingsDraft.postStyle}
              onChange={(event) => onSettingsDraftChange({ postStyle: event.target.value })}
              placeholder="Storytelling, contrarian, list post..."
            />
          </div>
          <div className="field-group">
            <div className="field-label">Preferred Length</div>
            <input
              className="field-input"
              value={settingsDraft.preferredPostLength}
              onChange={(event) => onSettingsDraftChange({ preferredPostLength: event.target.value })}
              placeholder="Short, medium, long"
            />
          </div>
        </div>
        <div className="field-group">
          <div className="field-label">Goals</div>
          <textarea
            className="field-input"
            rows={3}
            value={settingsDraft.contentGoals}
            onChange={(event) => onSettingsDraftChange({ contentGoals: event.target.value })}
            placeholder="Brand building, hiring, lead generation..."
          />
        </div>
        <div className="field-group">
          <div className="field-label">Topics to Avoid</div>
          <textarea
            className="field-input"
            rows={3}
            value={settingsDraft.topicsToAvoid}
            onChange={(event) => onSettingsDraftChange({ topicsToAvoid: event.target.value })}
            placeholder="Anything that should never appear in your posts"
          />
        </div>
        <button className="generate-btn" type="button" disabled={isSaving} onClick={onSavePreferences}>
          {isSaving ? "Saving preferences..." : "Save Preferences"}
        </button>
        {selectedNiche ? (
          <div style={{ marginTop: 14, fontSize: 12, color: "var(--text3)" }}>
            Suggested niche: {selectedNiche.name}
          </div>
        ) : null}
      </div>

      <div className="voice-grid" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div className="voice-card">
          <div className="section-title serif">Voice Profile</div>
          {voiceProfile ? (
            <div style={{ fontSize: 12, color: "var(--text3)", marginBottom: 12 }}>
              {voiceProfile.sample_count} samples captured · confidence {voiceProfile.confidence_score}/100
            </div>
          ) : null}
          <div className="field-group">
            <div className="field-label">Summary</div>
            <textarea
              className="field-input"
              rows={4}
              value={voiceDraft.summary}
              onChange={(event) => onVoiceDraftChange({ summary: event.target.value })}
              placeholder="Describe the core of your voice..."
            />
          </div>
          <div className="field-group">
            <div className="field-label">Traits</div>
            <textarea
              className="field-input"
              rows={3}
              value={voiceDraft.traits}
              onChange={(event) => onVoiceDraftChange({ traits: event.target.value })}
              placeholder="Concise, reflective, practical..."
            />
          </div>
          <div className="field-group">
            <div className="field-label">Banned Phrases</div>
            <textarea
              className="field-input"
              rows={3}
              value={voiceDraft.bannedPhrases}
              onChange={(event) => onVoiceDraftChange({ bannedPhrases: event.target.value })}
              placeholder="thrilled to share, game-changing..."
            />
          </div>
          <div className="field-group">
            <div className="field-label">Confidence</div>
            <input
              className="field-input"
              type="number"
              min={0}
              max={100}
              value={voiceDraft.confidenceScore}
              onChange={(event) => onVoiceDraftChange({ confidenceScore: event.target.value })}
            />
          </div>
          <button className="out-btn" type="button" disabled={isSaving} onClick={() => onSaveVoiceProfile(buildVoiceProfilePayload(voiceDraft))}>
            {isSaving ? "Saving..." : "Save Voice Profile"}
          </button>
        </div>

        <div className="voice-card">
          <div className="section-title serif">Writing Samples</div>
          <div style={{ display: "grid", gap: 8, marginBottom: 12 }}>
            {writingSamples.length > 0 ? (
              writingSamples.slice(0, 3).map((sample) => (
                <div key={sample.id} className="sample-box">
                  <div style={{ fontSize: 11, color: "var(--text3)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    {sample.title ?? "Untitled"}
                  </div>
                  <div style={{ fontSize: 13, color: "var(--text2)", lineHeight: 1.6 }}>
                    {sample.body}
                  </div>
                </div>
              ))
            ) : (
              <div style={{ fontSize: 12, color: "var(--text3)" }}>No samples saved yet.</div>
            )}
          </div>
          <div className="field-group">
            <div className="field-label">Add Sample</div>
            <input
              className="field-input"
              value={sampleDraft.title}
              onChange={(event) => onSampleDraftChange({ title: event.target.value })}
              placeholder="Sample title"
            />
            <textarea
              className="field-input"
              rows={4}
              style={{ marginTop: 8 }}
              value={sampleDraft.body}
              onChange={(event) => onSampleDraftChange({ body: event.target.value })}
              placeholder="Paste a LinkedIn post you wrote..."
            />
            <input
              className="field-input"
              style={{ marginTop: 8 }}
              value={sampleDraft.source}
              onChange={(event) => onSampleDraftChange({ source: event.target.value })}
              placeholder="Source"
            />
          </div>
          <button className="out-btn" type="button" disabled={isSaving} onClick={onSaveWritingSample}>
            {isSaving ? "Saving sample..." : "Save Sample"}
          </button>
          {selectedNiche ? (
            <div style={{ marginTop: 16, background: "var(--surface3)", border: "1px solid var(--border)", borderRadius: "var(--r8)", padding: 12 }}>
              <div style={{ fontSize: 11, color: "var(--gold)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Recommended niche
              </div>
              <div style={{ fontSize: 13, color: "var(--text2)", lineHeight: 1.6 }}>
                {selectedNiche.name}: {selectedNiche.description ?? "No description available."}
              </div>
            </div>
          ) : null}
        </div>
      </div>
      {isLoading ? <div style={{ fontSize: 12, color: "var(--text3)" }}>Loading settings...</div> : null}

      <div className="voice-card" style={{ borderColor: "rgba(220, 53, 69, 0.3)" }}>
        <div className="section-title serif" style={{ color: "var(--text2)" }}>Account</div>
        <p style={{ fontSize: 12, color: "var(--text3)", marginBottom: 14, lineHeight: 1.6 }}>
          Sign out of your Qalam account on this device.
        </p>
        <button
          className="out-btn"
          type="button"
          style={{
            background: "rgba(220, 53, 69, 0.1)",
            borderColor: "rgba(220, 53, 69, 0.4)",
            color: "#fa5555",
            width: "100%",
            justifyContent: "center",
          }}
          onClick={onLogout}
        >
          Sign out of account
        </button>
      </div>
    </div>
  );
}

export interface SettingsDraft {
  nicheSlug: string;
  targetAudience: string;
  contentGoals: string;
  tone: string;
  language: string;
  postStyle: string;
  ctaPreference: string;
  hashtagPolicy: string;
  emojiPolicy: string;
  topicsToAvoid: string;
  preferredPostLength: string;
}

export interface VoiceDraft {
  summary: string;
  traits: string;
  bannedPhrases: string;
  confidenceScore: string;
}

export interface WritingSampleDraft {
  title: string;
  body: string;
  source: string;
}

function buildVoiceProfilePayload(draft: VoiceDraft): VoiceProfileInput {
  return {
    summary: draft.summary.trim() || null,
    traits: draft.traits
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
    banned_phrases: draft.bannedPhrases
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
    confidence_score: Number.parseInt(draft.confidenceScore, 10) || 0,
  };
}

function Donut() {
  return (
    <svg width="120" height="120" viewBox="0 0 120 120" aria-label="Content mix chart">
      <circle cx="60" cy="60" r="40" fill="none" stroke="var(--border)" strokeWidth="20" />
      <circle cx="60" cy="60" r="40" fill="none" stroke="var(--gold)" strokeWidth="20" strokeDasharray="100 151" strokeDashoffset="-10" />
      <circle cx="60" cy="60" r="40" fill="none" stroke="var(--teal)" strokeWidth="20" strokeDasharray="60 151" strokeDashoffset="-110" />
      <circle cx="60" cy="60" r="40" fill="none" stroke="var(--teal-light)" strokeWidth="20" strokeDasharray="40 151" strokeDashoffset="-170" />
      <text x="60" y="56" textAnchor="middle" fontSize="11" fill="var(--text2)" fontFamily="var(--font-dm-sans)">Posts</text>
      <text x="60" y="70" textAnchor="middle" fontSize="14" fontWeight="500" fill="var(--gold)" fontFamily="var(--font-dm-sans)">47</text>
    </svg>
  );
}
