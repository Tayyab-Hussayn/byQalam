export function Notification({
  notification,
  onClose,
}: {
  notification: { icon: string; message: string } | null;
  onClose: () => void;
}) {
  return (
    <div className={`notif ${notification ? "show" : ""}`}>
      <span className="notif-icon">{notification?.icon ?? "✦"}</span>
      <span>{notification?.message ?? "Post generated successfully"}</span>
      <button className="notif-close" type="button" onClick={onClose} aria-label="Close notification">
        ×
      </button>
    </div>
  );
}
