import type { Latencies } from "../lib/types";

interface Props {
  latencies: Latencies;
}

const STAGES: { key: keyof Latencies; label: string; color: string }[] = [
  { key: "vision_ms", label: "Vision", color: "bg-violet-500" },
  { key: "match_ms", label: "Match", color: "bg-blue-500" },
  { key: "quote_ms", label: "Quote", color: "bg-amber-500" },
  { key: "reply_ms", label: "Reply", color: "bg-emerald-500" },
];

export function LatencyBars({ latencies }: Props) {
  const total = Object.values(latencies).reduce((s, v) => s + v, 0);

  return (
    <div className="mt-3 space-y-1">
      <p className="text-xs text-gray-400 dark:text-gray-500">
        Latencia total: <span className="font-semibold text-gray-700 dark:text-gray-300">{total} ms</span>
      </p>
      <div className="flex gap-0.5 h-2 rounded overflow-hidden">
        {STAGES.map(({ key, color }) => {
          const pct = total > 0 ? (latencies[key] / total) * 100 : 0;
          return (
            <div
              key={key}
              className={`${color} h-full`}
              style={{ width: `${pct}%` }}
              title={`${key}: ${latencies[key]} ms`}
            />
          );
        })}
      </div>
      <div className="flex flex-wrap gap-x-3 gap-y-0.5">
        {STAGES.map(({ key, label, color }) => (
          <span key={key} className="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
            <span className={`inline-block w-2 h-2 rounded-sm ${color}`} />
            {label}: {latencies[key]} ms
          </span>
        ))}
      </div>
    </div>
  );
}
