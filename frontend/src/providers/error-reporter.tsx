"use client";

import { useEffect } from "react";
import { sendClientError } from "@/lib/error-reporting";

export function ErrorReporter() {
  useEffect(() => {
    function handleError(event: ErrorEvent) {
      sendClientError({
        kind: "error",
        message: event.message || "Unhandled browser error",
        stack: event.error instanceof Error ? event.error.stack ?? null : null,
        filename: event.filename ?? null,
        line: event.lineno ?? null,
        column: event.colno ?? null,
        url: window.location.href,
        user_agent: window.navigator.userAgent,
      });
    }

    function handleRejection(event: PromiseRejectionEvent) {
      const reason = event.reason instanceof Error ? event.reason : new Error(String(event.reason));
      sendClientError({
        kind: "unhandledrejection",
        message: reason.message || "Unhandled promise rejection",
        stack: reason.stack ?? null,
        filename: null,
        line: null,
        column: null,
        url: window.location.href,
        user_agent: window.navigator.userAgent,
      });
    }

    window.addEventListener("error", handleError);
    window.addEventListener("unhandledrejection", handleRejection);

    return () => {
      window.removeEventListener("error", handleError);
      window.removeEventListener("unhandledrejection", handleRejection);
    };
  }, []);

  return null;
}
