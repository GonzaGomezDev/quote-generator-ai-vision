interface Props {
  latencies: Record<string, number>;
}

const TOOL_LABELS: Record<string, string> = {
  analyze_product_image_ms: "Vision",
  search_catalog_ms: "Búsqueda",
  build_quote_ms: "Cotización",
};

export function LatencyBars({ latencies }: Props) {
  const agentMs = latencies.agent_ms ?? 0;
  const replyMs = latencies.reply_ms ?? 0;
  const total = agentMs + replyMs;

  const toolEntries = Object.entries(latencies).filter(
    ([k]) => k !== "agent_ms" && k !== "reply_ms"
  );

  const agentPct = total > 0 ? (agentMs / total) * 100 : 0;
  const replyPct = total > 0 ? (replyMs / total) * 100 : 0;

  return (
    <div className="mt-3 space-y-1.5">
      <p className="text-xs text-gray-400 dark:text-gray-500">
        Latencia total:{" "}
        <span className="font-semibold text-gray-700 dark:text-gray-300">{total} ms</span>
      </p>

      {/* Stacked bar: Agent + Reply */}
      <div className="flex gap-0.5 h-2 rounded overflow-hidden w-full">
        <div
          className="bg-violet-500 h-full"
          style={{ width: `${agentPct}%` }}
          title={`Agente: ${agentMs} ms`}
        />
        <div
          className="bg-emerald-500 h-full"
          style={{ width: `${replyPct}%` }}
          title={`Envío: ${replyMs} ms`}
        />
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-x-3 gap-y-0.5">
        <span className="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
          <span className="inline-block w-2 h-2 rounded-sm bg-violet-500" />
          Agente: {agentMs} ms
        </span>
        <span className="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
          <span className="inline-block w-2 h-2 rounded-sm bg-emerald-500" />
          Envío: {replyMs} ms
        </span>
      </div>

      {/* Tool breakdown */}
      {toolEntries.length > 0 && (
        <div className="flex flex-wrap gap-x-3 gap-y-0.5 pt-0.5">
          {toolEntries.map(([key, ms]) => (
            <span key={key} className="text-xs text-gray-400 dark:text-gray-500">
              {TOOL_LABELS[key] ?? key.replace("_ms", "")}: {ms} ms
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
