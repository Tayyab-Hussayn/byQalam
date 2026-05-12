import type { DashboardView } from "@/types/dashboard";
import { dashboardSubtitles, dashboardTitles } from "../dashboardConfig";

export function Topbar({
  view,
  showNotif,
}: {
  view: DashboardView;
  showNotif: (icon: string, message: string) => void;
}) {
  return (
    <div className="topbar">
      <div className="topbar-left">
        <h1 className="serif">{dashboardTitles[view]}</h1>
        <p>{dashboardSubtitles[view]}</p>
      </div>
      <div className="topbar-right">
        <button className="icon-btn" title="Notifications" type="button" onClick={() => showNotif("🔔", "3 posts scheduled for this week. Golden window closes in 42 minutes.")}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M8 1a5 5 0 015 5v3l1.5 2H1.5L3 9V6a5 5 0 015-5zM6 13a2 2 0 004 0" /></svg>
        </button>
        <button className="icon-btn" title="Search" type="button">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="6.5" cy="6.5" r="5" /><path d="M10 10l4 4" /></svg>
        </button>
        <button className="avatar" type="button" onClick={() => showNotif("👤", "Profile: Zara Hussain · Head of Growth · 847 posts generated")}>ZH</button>
      </div>
    </div>
  );
}
