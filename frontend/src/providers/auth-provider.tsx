"use client";

import { useEffect } from "react";
import { supabase } from "@/lib/auth/supabase";
import { setAccessToken } from "@/lib/auth/session";

async function syncSessionCookie(accessToken: string) {
  await fetch("/api/auth/session-sync", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ accessToken }),
  });
}

async function clearSessionCookie() {
  await fetch("/api/auth/session-clear", {
    method: "POST",
    credentials: "include",
  });
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    let active = true;

    const loadSession = async () => {
      const { data } = await supabase.auth.getSession();
      if (!active) return;
      const token = data.session?.access_token ?? null;
      setAccessToken(token);
      if (token) {
        await syncSessionCookie(token);
      } else {
        await clearSessionCookie();
      }
    };

    void loadSession();

    const { data: subscription } = supabase.auth.onAuthStateChange(async (_event, session) => {
      const token = session?.access_token ?? null;
      setAccessToken(token);
      if (token) {
        await syncSessionCookie(token);
        return;
      }
      await clearSessionCookie();
    });

    return () => {
      active = false;
      subscription.subscription.unsubscribe();
    };
  }, []);

  return children;
}
