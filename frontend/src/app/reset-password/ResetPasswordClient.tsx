"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { supabase } from "@/lib/auth/supabase";

export default function ResetPasswordClient() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const canSubmit = useMemo(
    () => Boolean(password.trim() && confirmPassword.trim() && password === confirmPassword),
    [password, confirmPassword]
  );

  async function handleReset() {
    if (!canSubmit || loading) return;
    if (!supabase) {
      setMessage("Auth system not configured. Please add Supabase environment variables.");
      return;
    }
    if (password.length < 6) {
      setMessage("Password must be at least 6 characters.");
      return;
    }
    setLoading(true);
    setMessage(null);
    try {
      const { error } = await supabase.auth.updateUser({ password });
      if (error) {
        setMessage(error.message);
        setLoading(false);
        return;
      }
      setSuccess(true);
      setLoading(false);
    } catch (err) {
      setMessage("An unexpected error occurred.");
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#060D0A] px-6 py-12 text-[#F0EDE6]">
      <section className="w-full max-w-md rounded-2xl border border-[rgba(201,146,42,0.25)] bg-[#0A1510] p-8 shadow-2xl">
        <Link href="/" className="mb-8 inline-block text-sm font-semibold text-[#C9922A]">
          Qalam.
        </Link>
        <h1 className="font-serif text-3xl text-[#F0EDE6]">Reset password</h1>
        <p className="mt-3 text-sm leading-6 text-[#B8B4AA]">
          {success
            ? "Your password has been reset successfully."
            : "Enter a new password for your account."}
        </p>
        <div className="mt-8 space-y-5">
          {!success && (
            <>
              <label className="block">
                <span className="text-xs uppercase tracking-[0.14em] text-[#7A7670]">New password</span>
                <input
                  className="mt-2 w-full rounded-lg border border-[rgba(201,146,42,0.15)] bg-[#0F1E17] px-4 py-3 text-sm outline-none transition focus:border-[#C9922A]"
                  name="password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                />
              </label>
              <label className="block">
                <span className="text-xs uppercase tracking-[0.14em] text-[#7A7670]">Confirm password</span>
                <input
                  className="mt-2 w-full rounded-lg border border-[rgba(201,146,42,0.15)] bg-[#0F1E17] px-4 py-3 text-sm outline-none transition focus:border-[#C9922A]"
                  name="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                />
              </label>
              {password && confirmPassword && password !== confirmPassword && (
                <p className="text-sm leading-6 text-[#E8B84B]">Passwords do not match.</p>
              )}
              {message ? <p className="text-sm leading-6 text-[#E8B84B]">{message}</p> : null}
              <button
                className="w-full rounded-lg bg-[#C9922A] px-4 py-3 text-sm font-semibold text-[#060D0A] transition hover:bg-[#E8B84B] disabled:cursor-not-allowed disabled:opacity-70"
                type="button"
                disabled={!canSubmit || loading}
                onClick={handleReset}
              >
                {loading ? "Resetting..." : "Reset password"}
              </button>
            </>
          )}
          {success && (
            <Link
              href="/login"
              className="mt-4 inline-block w-full rounded-lg bg-[#C9922A] px-4 py-3 text-center text-sm font-semibold text-[#060D0A] transition hover:bg-[#E8B84B]"
            >
              Back to login
            </Link>
          )}
        </div>
      </section>
    </main>
  );
}