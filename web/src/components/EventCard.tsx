import { useState } from "react";
import type { PipelineEvent } from "../lib/types";
import { ChannelBadge } from "./ChannelBadge";
import { LatencyBars } from "./LatencyBars";

interface Props {
  event: PipelineEvent;
}

export function EventCard({ event }: Props) {
  const [expanded, setExpanded] = useState(false);
  const { extraction, quote, latencies } = event;
  const matched = quote !== null;

  return (
    <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] p-4 flex gap-4">
      {/* Thumbnail */}
      <div className="flex-shrink-0">
        <img
          src={event.media_url}
          alt="product"
          className="w-20 h-20 object-cover rounded-lg border border-gray-200 dark:border-gray-700"
          onError={(e) => {
            (e.target as HTMLImageElement).src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80'%3E%3Crect width='80' height='80' fill='%231e293b'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-size='28' fill='%2364748b'%3E📦%3C/text%3E%3C/svg%3E";
          }}
        />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2 flex-wrap">
            <ChannelBadge channel={event.channel} />
            <span className="text-xs text-gray-400 dark:text-gray-500">{event.sender}</span>
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                matched
                  ? "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400"
                  : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
              }`}
            >
              {matched ? "Con cotización" : "Sin cotización"}
            </span>
          </div>
          <span className="text-xs text-gray-400 dark:text-gray-500">
            {new Date(event.received_at).toLocaleTimeString()}
          </span>
        </div>

        {/* Product info */}
        <p className="mt-2 font-semibold text-gray-800 dark:text-white truncate">
          {extraction.product_guess}
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {[extraction.brand, extraction.category, extraction.color]
            .filter(Boolean)
            .join(" · ")}
          {" · "}
          <span className="text-gray-400 dark:text-gray-500">
            {Math.round(extraction.confidence * 100)}% confianza
          </span>
        </p>

        {/* Quote summary */}
        {quote && (
          <div className="mt-2 flex items-baseline gap-3">
            <span className="text-lg font-bold text-success-600 dark:text-success-400">
              ${quote.total.toFixed(2)} {quote.currency}
            </span>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {quote.sku_name} × {quote.quantity}
            </span>
          </div>
        )}

        {/* Latency bars */}
        <LatencyBars latencies={latencies} />

        {/* Expandable raw JSON */}
        <button
          onClick={() => setExpanded((v) => !v)}
          className="mt-2 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
        >
          {expanded ? "▲ Ocultar" : "▼ Extracción raw"}
        </button>
        {expanded && (
          <pre className="mt-2 text-xs bg-gray-50 dark:bg-gray-800 rounded-lg p-3 overflow-x-auto text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700">
            {JSON.stringify(extraction, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
