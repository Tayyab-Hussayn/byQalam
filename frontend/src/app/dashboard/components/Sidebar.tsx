import type { DashboardView } from "@/types/dashboard";
import { LogoIcon, NavIcon } from "./DashboardIcons";

export function Sidebar({
  view,
  setView,
  showNotif,
  planName = "Pro Plan",
  planDescription = "100 posts/day · Claude Sonnet · Advanced analytics",
}: {
  view: DashboardView;
  setView: (view: DashboardView) => void;
  showNotif: (icon: string, message: string) => void;
  planName?: string;
  planDescription?: string;
}) {
  const itemClass = (target: DashboardView) => `nav-item ${view === target ? "active" : ""}`;

  return (
    <aside className="sidebar">
      <div className="logo-area">
        <div className="logo-mark">
          <LogoIcon />
          <div>
            <div className="logo-text">Qalam</div>
            <div className="logo-sub">Voice Engine v2</div>
          </div>
        </div>
      </div>
      <div className="nav-section">
        <div className="nav-label">Workspace</div>
        <button type="button" className={itemClass("dashboard")} onClick={() => setView("dashboard")}><NavIcon kind="dashboard" />Dashboard</button>
        <button type="button" className={itemClass("writer")} onClick={() => setView("writer")}><NavIcon kind="writer" />AI Writer<span className="nav-badge">New</span></button>
        <button type="button" className="nav-item" onClick={() => setView("dashboard")}><NavIcon kind="calendar" />Content Calendar</button>
        <button type="button" className="nav-item" onClick={() => setView("dashboard")}><NavIcon kind="library" />Library</button>
      </div>
      <div className="nav-section">
        <div className="nav-label">Intelligence</div>
        <button type="button" className={itemClass("voice")} onClick={() => setView("voice")}><NavIcon kind="voice" />Voice Fingerprint</button>
        <button type="button" className={itemClass("analytics")} onClick={() => setView("analytics")}><NavIcon kind="analytics" />Analytics</button>
        <button type="button" className="nav-item" onClick={() => setView("dashboard")}><NavIcon kind="plus" />Templates</button>
      </div>
      <div className="nav-section">
        <div className="nav-label">Account</div>
        <button type="button" className={itemClass("integrations")} onClick={() => setView("integrations")}><NavIcon kind="link" />LinkedIn & Billing</button>
        <button type="button" className={itemClass("settings")} onClick={() => setView("settings")}><NavIcon kind="settings" />Settings</button>
      </div>
      <div className="sidebar-footer">
        <div className="plan-card">
          <div className="plan-name">{planName}</div>
          <div className="plan-desc">{planDescription}</div>
          <button className="upgrade-btn" type="button" onClick={() => showNotif("🚀", "Agency plan unlocks 5 client profiles + white-label export!")}>Upgrade to Agency →</button>
        </div>
      </div>
    </aside>
  );
}
