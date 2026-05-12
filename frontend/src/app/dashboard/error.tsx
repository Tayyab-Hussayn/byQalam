"use client";

import Link from "next/link";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#060D0A] px-6 text-[#F0EDE6]">
      <section className="max-w-lg rounded-2xl border border-[rgba(201,146,42,0.25)] bg-[#0A1510] p-8 shadow-[0_24px_80px_rgba(0,0,0,0.4)]">
        <p className="text-xs uppercase tracking-[0.18em] text-[#C9922A]">Dashboard unavailable</p>
        <h1 className="mt-3 font-serif text-3xl font-normal">Qalam could not load the dashboard</h1>
        <p className="mt-3 text-sm leading-6 text-[#B8B4AA]">
          {error.message}
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <button
            className="rounded-lg bg-[#C9922A] px-4 py-3 text-sm font-semibold text-[#060D0A]"
            onClick={reset}
            type="button"
          >
            Try again
          </button>
          <Link
            className="rounded-lg border border-[rgba(201,146,42,0.25)] px-4 py-3 text-sm text-[#F0EDE6]"
            href="/dashboard"
          >
            Go back
          </Link>
        </div>
      </section>
    </main>
  );
}
