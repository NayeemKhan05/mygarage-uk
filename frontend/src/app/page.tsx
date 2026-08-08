import { getBackendStatus } from "@/lib/api";

export default async function Home() {
  const backendStatus = await getBackendStatus();

  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-16">
      <p className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-zinc-500">
        Initial build
      </p>
      <h1 className="text-5xl font-bold tracking-tight">MyGarage UK</h1>
      <p className="mt-5 max-w-2xl text-lg leading-8 text-zinc-600">
        A personal hub for UK vehicle history, MOT data, servicing and maintenance insights.
      </p>

      <div className="mt-10 grid gap-4 sm:grid-cols-3">
        <StatusCard label="Frontend" value="online" />
        <StatusCard label="Backend" value={backendStatus} />
        <StatusCard label="Database" value="next" />
      </div>
    </main>
  );
}

function StatusCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
      <p className="text-sm text-zinc-500">{label}</p>
      <p className="mt-2 text-xl font-semibold capitalize">{value}</p>
    </div>
  );
}
