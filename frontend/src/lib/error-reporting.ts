export interface ClientErrorEvent {
  kind: "error" | "unhandledrejection";
  message: string;
  stack?: string | null;
  filename?: string | null;
  line?: number | null;
  column?: number | null;
  url: string;
  user_agent: string;
  timestamp: string;
}

export function serializeClientError(input: Omit<ClientErrorEvent, "timestamp">): string {
  return JSON.stringify({
    ...input,
    timestamp: new Date().toISOString(),
  });
}

export function sendClientError(payload: Omit<ClientErrorEvent, "timestamp">) {
  const body = serializeClientError(payload);
  const endpoint = "/api/errors/client";

  if (typeof navigator !== "undefined" && "sendBeacon" in navigator) {
    const blob = new Blob([body], { type: "application/json" });
    if (navigator.sendBeacon(endpoint, blob)) {
      return;
    }
  }

  void fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
    keepalive: true,
  }).catch(() => undefined);
}
