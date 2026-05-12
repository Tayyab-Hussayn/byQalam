import Link from "next/link";

export default function DashboardNotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#060D0A] px-6 text-[#F0EDE6]">
      <section className="max-w-md rounded-2xl border border-[rgba(201,146,42,0.25)] bg-[#0A1510] p-8">
        <p className="text-xs uppercase tracking-[0.18em] text-[#C9922A]">Dashboard page not found</p>
        <h1 className="mt-3 font-serif text-3xl font-normal">This dashboard route does not exist</h1>
        <p className="mt-3 text-sm leading-6 text-[#B8B4AA]">
          The route may have changed or the workspace view was removed.
        </p>
        <Link
          className="mt-6 inline-flex rounded-lg bg-[#C9922A] px-4 py-3 text-sm font-semibold text-[#060D0A]"
          href="/dashboard"
        >
          Back to dashboard
        </Link>
      </section>
    </main>
  );
}
