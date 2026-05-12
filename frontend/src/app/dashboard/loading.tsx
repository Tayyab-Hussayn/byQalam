export default function DashboardLoading() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#060D0A] px-6 text-[#F0EDE6]">
      <div className="w-full max-w-4xl rounded-2xl border border-[rgba(201,146,42,0.25)] bg-[#0A1510] p-6 shadow-[0_24px_80px_rgba(0,0,0,0.4)]">
        <div className="h-4 w-36 animate-pulse rounded-full bg-[#142618]" />
        <div className="mt-6 grid gap-4 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div
              key={index}
              className="h-24 animate-pulse rounded-xl border border-[rgba(201,146,42,0.12)] bg-[#0F1E17]"
            />
          ))}
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-[1fr_380px]">
          <div className="h-80 animate-pulse rounded-xl border border-[rgba(201,146,42,0.12)] bg-[#0F1E17]" />
          <div className="h-80 animate-pulse rounded-xl border border-[rgba(201,146,42,0.12)] bg-[#0F1E17]" />
        </div>
      </div>
    </main>
  );
}
