"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/auth/supabase";

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.85H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z" fill="#4285F4"/>
      <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" fill="#34A853"/>
      <path d="M4.964 10.71A5.41 5.41 0 0 1 4.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.139.413 2.217 1.09 3.042l3.874-2.332z" fill="#FBBC05"/>
      <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L4.964 7.29C5.672 5.163 7.656 3.58 9 3.58z" fill="#EA4335"/>
    </svg>
  );
}

export default function RegisterClient({ nextPath }: { nextPath: string }) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState<"signup" | "google" | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const canSubmit = useMemo(() => Boolean(email.trim() && password.trim()), [email, password]);

  async function handleSignUp() {
    if (!canSubmit || loading) return;
    if (!supabase) {
      setMessage("Auth system not configured. Please add Supabase environment variables.");
      return;
    }
    if (password.length < 8) {
      setMessage("Password must be at least 8 characters.");
      return;
    }
    setLoading("signup");
    setMessage(null);
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      });
      if (error) {
        setMessage(error.message);
        setLoading(null);
        return;
      }
      if (data.session?.access_token) {
        router.push(nextPath);
        router.refresh();
        return;
      }
      setMessage("Check your email to confirm your account before continuing.");
      setLoading(null);
    } catch (err) {
      setMessage("An unexpected error occurred.");
      setLoading(null);
    }
  }

  async function handleGoogleSignIn() {
    if (loading || !supabase) {
      setMessage("Auth system not configured. Please add Supabase environment variables.");
      return;
    }
    setLoading("google");
    setMessage(null);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${window.location.origin}/api/auth/session-sync?next=${encodeURIComponent(nextPath)}`,
        },
      });
      if (error) {
        setMessage(error.message);
        setLoading(null);
        return;
      }
    } catch (err) {
      setMessage("An unexpected error occurred.");
      setLoading(null);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#060D0A] px-6 py-12 text-[#F0EDE6]">
      <section className="w-full max-w-md rounded-2xl border border-[rgba(201,146,42,0.25)] bg-[#0A1510] p-8 shadow-2xl">
        <Link href="/" className="mb-8 inline-block text-sm font-semibold text-[#C9922A]">
          Qalam.
        </Link>
        <h1 className="font-serif text-3xl text-[#F0EDE6]">Create your account</h1>
        <p className="mt-3 text-sm leading-6 text-[#B8B4AA]">
          Get started with Qalam to generate LinkedIn content in your voice.
        </p>
        <div className="mt-8 space-y-5">
          <button
            className="flex w-full items-center justify-center gap-3 rounded-lg border border-[rgba(201,146,42,0.25)] bg-transparent px-4 py-3 text-sm font-semibold text-[#F0EDE6] transition hover:border-[#C9922A] disabled:cursor-not-allowed disabled:opacity-70"
            type="button"
            disabled={loading !== null}
            onClick={handleGoogleSignIn}
          >
            <GoogleIcon />
            {loading === "google" ? "Signing up..." : "Continue with Google"}
          </button>
          <div className="flex items-center gap-3">
            <div className="h-px flex-1 bg-[rgba(201,146,42,0.15)]" />
            <span className="text-xs uppercase tracking-wider text-[#7A7670]">or</span>
            <div className="h-px flex-1 bg-[rgba(201,146,42,0.15)]" />
          </div>
          <label className="block">
            <span className="text-xs uppercase tracking-[0.14em] text-[#7A7670]">Email</span>
            <input
              className="mt-2 w-full rounded-lg border border-[rgba(201,146,42,0.15)] bg-[#0F1E17] px-4 py-3 text-sm outline-none transition focus:border-[#C9922A]"
              name="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label className="block">
            <span className="text-xs uppercase tracking-[0.14em] text-[#7A7670]">Password</span>
            <input
              className="mt-2 w-full rounded-lg border border-[rgba(201,146,42,0.15)] bg-[#0F1E17] px-4 py-3 text-sm outline-none transition focus:border-[#C9922A]"
              name="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
            <span className="mt-1 block text-xs text-[#7A7670]">Use 8 or more characters</span>
          </label>
          {message ? <p className="text-sm leading-6 text-[#E8B84B]">{message}</p> : null}
          <button
            className="w-full rounded-lg bg-[#C9922A] px-4 py-3 text-sm font-semibold text-[#060D0A] transition hover:bg-[#E8B84B] disabled:cursor-not-allowed disabled:opacity-70"
            type="button"
            disabled={!canSubmit || loading !== null}
            onClick={handleSignUp}
          >
            {loading === "signup" ? "Creating account..." : "Create account"}
          </button>
          <p className="text-center text-sm text-[#B8B4AA]">
            Already have an account?{" "}
            <Link href="/login" className="text-[#C9922A] hover:underline">
              Log in
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}