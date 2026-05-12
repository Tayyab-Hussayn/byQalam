export function SparkIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
      <path d="M8 1l1.8 5.4L15 8l-5.2 1.6L8 15 6.2 9.6 1 8l5.2-1.6z" />
    </svg>
  );
}

export function LogoIcon() {
  return (
    <svg className="logo-icon" viewBox="0 0 100 100" fill="none" aria-hidden="true">
      <circle cx="50" cy="48" r="40" stroke="#C9922A" strokeWidth="8" />
      <path d="M50 22 C50 22, 38 36, 38 48 C38 55 43.5 61 50 61 C56.5 61 62 55 62 48 C62 36 50 22 50 22Z" fill="#C9922A" />
      <path d="M50 44 C50 44, 44 50, 44 54 C44 57.3 46.7 60 50 60 C53.3 60 56 57.3 56 54 C56 50 50 44 50 44Z" fill="#0D5C4A" />
      <path d="M30 78 Q45 72 55 76 Q65 80 72 74" stroke="#C9922A" strokeWidth="5" strokeLinecap="round" fill="none" />
    </svg>
  );
}

export function NavIcon({
  kind,
}: {
  kind:
    | "dashboard"
    | "writer"
    | "calendar"
    | "library"
    | "voice"
    | "analytics"
    | "plus"
    | "settings"
    | "link";
}) {
  if (kind === "dashboard") {
    return <svg className="nav-icon" viewBox="0 0 16 16" fill="currentColor"><rect x="1" y="1" width="6" height="6" rx="1.5" /><rect x="9" y="1" width="6" height="6" rx="1.5" /><rect x="1" y="9" width="6" height="6" rx="1.5" /><rect x="9" y="9" width="6" height="6" rx="1.5" /></svg>;
  }
  if (kind === "writer") {
    return <svg className="nav-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M13.5 1.5a1.5 1.5 0 00-2.12 0l-8 8L2 14l4.5-1.38 8-8a1.5 1.5 0 000-2.12z" /></svg>;
  }
  if (kind === "calendar") {
    return <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="1" y="3" width="14" height="11" rx="1.5" /><path d="M5 1v4M11 1v4M1 7h14" /></svg>;
  }
  if (kind === "library") {
    return <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M2 12h12M2 8h9M2 4h6" /></svg>;
  }
  if (kind === "voice") {
    return <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><ellipse cx="8" cy="5" rx="3" ry="4" /><path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6" /></svg>;
  }
  if (kind === "analytics") {
    return <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M2 14l3-4 3 2 3-6 3 4" /></svg>;
  }
  if (kind === "plus") {
    return <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M8 1v14M1 8h14" /></svg>;
  }
  if (kind === "link") {
    return <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M6 10l4-4" /><path d="M5 5l-2 2a3 3 0 104 4l1-1" /><path d="M11 11l2-2a3 3 0 10-4-4l-1 1" /></svg>;
  }
  return <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="8" cy="8" r="7" /><path d="M8 7v5M8 5v.5" /></svg>;
}
