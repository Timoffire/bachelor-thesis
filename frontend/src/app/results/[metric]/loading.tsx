// src/app/results/[metric]/loading.tsx
export default function LoadingMetric() {
  return (
    <div className="animate-pulse rounded-3xl border border-white/10 bg-white/5 p-6">
      <div className="h-6 w-48 bg-white/10 rounded mb-2" />
      <div className="h-4 w-64 bg-white/10 rounded" />
      <div className="mt-6 h-40 bg-white/10 rounded-2xl" />
      <div className="mt-6 h-24 bg-white/10 rounded-2xl" />
    </div>
  );
}
