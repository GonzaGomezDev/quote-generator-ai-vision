import { useEffect, useState } from "react";
import type { ChannelFilter, MatchFilter, PipelineEvent } from "../lib/types";
import { useApi } from "../hooks/useApi";
import { ChannelBadge } from "../components/ChannelBadge";

export default function QuoteHistoryPage() {
  const [events, setEvents] = useState<PipelineEvent[]>([]);
  const [channel, setChannel] = useState<ChannelFilter>("all");
  const [match, setMatch] = useState<MatchFilter>("all");
  const [loading, setLoading] = useState(true);
  const { apiFetch } = useApi();

  useEffect(() => {
    apiFetch("/api/quotes?limit=200")
      .then((data: PipelineEvent[]) => setEvents(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [apiFetch]);

  const filtered = events.filter((e) => {
    if (channel !== "all" && e.channel !== channel) return false;
    if (match === "matched" && !e.quote) return false;
    if (match === "unmatched" && e.quote) return false;
    return true;
  });

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Historial de Cotizaciones</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Todas las solicitudes de imagen procesadas</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 mb-4">
        {(["all", "whatsapp", "telegram"] as ChannelFilter[]).map((v) => (
          <button
            key={v}
            onClick={() => setChannel(v)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              channel === v
                ? "bg-brand-500 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700"
            }`}
          >
            {v}
          </button>
        ))}
        <div className="w-px h-7 bg-gray-200 dark:bg-gray-700 self-center mx-1" />
        {(["all", "matched", "unmatched"] as MatchFilter[]).map((v) => (
          <button
            key={v}
            onClick={() => setMatch(v)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              match === v
                ? "bg-brand-500 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700"
            }`}
          >
            {v}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] overflow-hidden">
        {loading ? (
          <div className="py-16 text-center text-gray-400">Cargando…</div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center text-gray-400">Sin eventos aún.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 dark:bg-white/[0.02] border-b border-gray-200 dark:border-gray-800">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-500 dark:text-gray-400">Hora</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500 dark:text-gray-400">Canal</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500 dark:text-gray-400">Remitente</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500 dark:text-gray-400">Producto Detectado</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500 dark:text-gray-400">Conf.</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500 dark:text-gray-400">Cotización</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500 dark:text-gray-400">Total ms</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {filtered.map((e) => {
                  const totalMs = Object.values(e.latencies).reduce((s, v) => s + v, 0);
                  return (
                    <tr key={e.message_id} className="hover:bg-gray-50 dark:hover:bg-white/[0.02]">
                      <td className="px-4 py-3 text-gray-500 dark:text-gray-400 whitespace-nowrap">
                        {new Date(e.received_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3">
                        <ChannelBadge channel={e.channel} />
                      </td>
                      <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{e.sender}</td>
                      <td className="px-4 py-3 text-gray-800 dark:text-white font-medium">
                        {e.extraction.product_guess}
                      </td>
                      <td className="px-4 py-3 text-gray-500 dark:text-gray-400">
                        {Math.round(e.extraction.confidence * 100)}%
                      </td>
                      <td className="px-4 py-3">
                        {e.quote ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400">
                            ${e.quote.total.toFixed(2)} {e.quote.currency}
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                            Sin coincidencia
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-500 dark:text-gray-400">{totalMs}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
