"use client";

import Link from "next/link";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body className="bg-[#060D0A] text-[#F0EDE6]">
        <main className="flex min-h-screen items-center justify-center px-6">
          <section className="max-w-lg rounded-2xl border border-[rgba(201,146,42,0.25)] bg-[#0A1510] p-8 shadow-[0_24px_80px_rgba(0,0,0,0.4)]">
            <p className="text-xs uppercase tracking-[0.18em] text-[#C9922A]">Application error</p>
            <h1 className="mt-3 font-serif text-3xl font-normal">Qalam hit an unexpected error</h1>
            <p className="mt-3 text-sm leading-6 text-[#B8B4AA]">{error.message}</p>
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
                Open dashboard
              </Link>
            </div>
          </section>
        </main>
      </body>
    </html>
  );
}
