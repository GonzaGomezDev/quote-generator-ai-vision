import { useState } from "react";
import type { AgentEvent, ToolCall } from "../lib/types";
import { ChannelBadge } from "./ChannelBadge";
import { LatencyBars } from "./LatencyBars";

interface Props {
  event: AgentEvent;
}

interface ChainStep {
  iconClass: string;
  label: string;
  detail?: string;
}

function buildChain(event: AgentEvent, hasImage: boolean, hasExtraction: boolean): ChainStep[] {
  const { tool_calls, quote } = event;
  const find = (name: string): ToolCall | undefined => tool_calls.find((t) => t.name === name);

  const steps: ChainStep[] = [];

  steps.push({
    iconClass: "lni-comments",
    label: "Mensaje recibido",
    detail: "",
  });

  const analyzeCall = find("analyze_product_image");
  if (analyzeCall || hasImage || hasExtraction) {
    steps.push({
      iconClass: "lni-image",
      label: "Imagen analizada",
      detail: ""
    });
  }

  const searchCall = find("search_catalog");
  if (searchCall) {
    steps.push({ iconClass: "lni-database", label: "Catálogo revisado", detail: searchCall.result_summary });
  }

  const quoteCall = find("build_quote");
  if (quoteCall || quote) {
    steps.push({
      iconClass: "lni-tag",
      label: "Cotización lista",
      detail: quote ? `$${quote.total.toFixed(2)} ${quote.currency}` : quoteCall?.result_summary,
    });
  }

  steps.push({ iconClass: "lni-checkmark-circle", label: "Respuesta enviada" });

  return steps;
}

const PLACEHOLDER_IMG =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80'%3E%3Crect width='80' height='80' fill='%231e293b'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-size='28' fill='%2364748b'%3E📦%3C/text%3E%3C/svg%3E";

export function EventCard({ event }: Props) {
  const [expanded, setExpanded] = useState(false);
  const { extraction, quote, latencies, tool_calls } = event;
  const hasImage = !!event.media_url;
  const hasExtraction = extraction && "product_guess" in extraction;

  return (
    <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] p-4 flex gap-4">
      {/* Thumbnail — only when an image was sent */}
      {hasImage && (
        <div className="flex-shrink-0">
          <img
            src={`/api/media/proxy?url=${encodeURIComponent(event.media_url!)}`}
            alt="product"
            className="w-20 h-20 object-cover rounded-lg border border-gray-200 dark:border-gray-700"
            onError={(e) => {
              (e.target as HTMLImageElement).src = PLACEHOLDER_IMG;
            }}
          />
        </div>
      )}

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2 flex-wrap">
            <ChannelBadge channel={event.channel} />
            <span className="text-xs text-gray-400 dark:text-gray-500">{event.sender}</span>
            {quote ? (
              <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400">
                Con cotización
              </span>
            ) : (
              <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                Sin cotización
              </span>
            )}
          </div>
          <span className="text-xs text-gray-400 dark:text-gray-500">
            {new Date(event.received_at).toLocaleTimeString()}
          </span>
        </div>

        {/* Inbound text message (if any) */}
        {event.text && (
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-800/60 rounded-lg px-3 py-2 border border-gray-100 dark:border-gray-700">
            {event.text}
          </p>
        )}

        {/* Vision extraction summary */}
        {hasExtraction && (
          <>
            <p className="mt-2 font-semibold text-gray-800 dark:text-white truncate">
              {(extraction as { product_guess: string }).product_guess}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {[(extraction as any).brand, (extraction as any).category, (extraction as any).color]
                .filter(Boolean)
                .join(" · ")}
              {" · "}
              <span className="text-gray-400 dark:text-gray-500">
                {Math.round((extraction as any).confidence * 100)}% confianza
              </span>
            </p>
          </>
        )}

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

        {/* Agent reply */}
        <div className="mt-3 rounded-lg bg-brand-50 dark:bg-brand-500/10 border border-brand-100 dark:border-brand-500/20 px-3 py-2">
          <p className="text-xs font-medium text-brand-600 dark:text-brand-400 mb-0.5">Respuesta del agente</p>
          <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{event.reply_text}</p>
        </div>

        {/* Latency bars */}
        <LatencyBars latencies={latencies} />

        {/* Process chain */}
        {(() => {
          const steps = buildChain(event, hasImage, hasExtraction);
          return (
            <div className="mt-4 flex items-start overflow-x-auto pb-1">
              {steps.map((step, i) => (
                <div key={i} className="flex items-center shrink-0">
                  <div className="flex flex-col items-center gap-1.5 w-[4.5rem]">
                    <div className="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-600 border border-gray-300 dark:border-gray-500 flex items-center justify-center">
                      <i className={`lni ${step.iconClass} text-lg text-gray-700 dark:text-white`} />
                    </div>
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-200 text-center leading-tight">
                      {step.label}
                    </span>
                    {step.detail && (
                      <span
                        className="text-[11px] text-gray-400 dark:text-gray-400 text-center leading-tight w-full truncate px-0.5"
                        title={step.detail}
                      >
                        {step.detail}
                      </span>
                    )}
                  </div>
                  {i < steps.length - 1 && (
                    <div className="h-px w-4 bg-gray-300 dark:bg-gray-500 shrink-0 mb-7" />
                  )}
                </div>
              ))}
            </div>
          );
        })()}

        {/* Expandable raw JSON */}
        <button
          onClick={() => setExpanded((v) => !v)}
          className="mt-3 text-sm text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
        >
          {expanded ? "▲ Ocultar" : "▼ Ver payload raw"}
        </button>
        {expanded && (
          <pre className="mt-2 text-xs bg-gray-50 dark:bg-gray-800 rounded-lg p-3 overflow-x-auto text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700">
            {JSON.stringify({ extraction, tool_calls, quote }, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
