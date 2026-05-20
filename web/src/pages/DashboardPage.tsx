import { useCallback, useEffect, useReducer, useState } from "react";
import type { ChannelFilter, MatchFilter, PipelineEvent } from "../lib/types";
import { useApi } from "../hooks/useApi";
import { useEventStream } from "../hooks/useEventStream";
import { EventCard } from "../components/EventCard";
import { Filters } from "../components/Filters";

type Action =
  | { type: "prepend"; event: PipelineEvent }
  | { type: "backfill"; events: PipelineEvent[] };

function reducer(state: PipelineEvent[], action: Action): PipelineEvent[] {
  if (action.type === "prepend") return [action.event, ...state].slice(0, 200);
  if (action.type === "backfill") return action.events;
  return state;
}

export default function DashboardPage() {
  const [events, dispatch] = useReducer(reducer, []);
  const [channel, setChannel] = useState<ChannelFilter>("all");
  const [match, setMatch] = useState<MatchFilter>("all");
  const { apiFetch } = useApi();

  useEffect(() => {
    apiFetch("/api/quotes?limit=50")
      .then((data: PipelineEvent[]) => dispatch({ type: "backfill", events: data }))
      .catch(console.error);
  }, [apiFetch]);

  const onEvent = useCallback((e: PipelineEvent) => {
    dispatch({ type: "prepend", event: e });
  }, []);
  useEventStream(onEvent);

  const filtered = events.filter((e) => {
    if (channel !== "all" && e.channel !== channel) return false;
    if (match === "matched" && !e.quote) return false;
    if (match === "unmatched" && e.quote) return false;
    return true;
  });

  const matched = events.filter((e) => e.quote !== null).length;
  const unmatched = events.length - matched;

  return (
    <div>
      {/* Stats row */}
      <div className="grid grid-cols-2 gap-4 mb-6 sm:grid-cols-4">
        <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
          <p className="text-sm text-gray-500 dark:text-gray-400">Total Eventos</p>
          <p className="mt-1 text-2xl font-semibold text-gray-800 dark:text-white">{events.length}</p>
        </div>
        <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
          <p className="text-sm text-gray-500 dark:text-gray-400">Con Cotización</p>
          <p className="mt-1 text-2xl font-semibold text-success-500">{matched}</p>
        </div>
        <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
          <p className="text-sm text-gray-500 dark:text-gray-400">Sin Cotización</p>
          <p className="mt-1 text-2xl font-semibold text-error-500">{unmatched}</p>
        </div>
        <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
          <p className="text-sm text-gray-500 dark:text-gray-400">Tasa de Coincidencia</p>
          <p className="mt-1 text-2xl font-semibold text-gray-800 dark:text-white">
            {events.length > 0 ? Math.round((matched / events.length) * 100) : 0}%
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-4 p-4 rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
        <Filters
          channel={channel}
          match={match}
          onChannel={setChannel}
          onMatch={setMatch}
          total={filtered.length}
        />
      </div>

      {/* Event feed */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] py-24 text-center">
            <p className="text-4xl mb-4">📭</p>
            <p className="text-lg text-gray-500 dark:text-gray-400">
              Esperando imágenes entrantes…
            </p>
            <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
              Enviá una foto de producto por WhatsApp o Instagram.
            </p>
          </div>
        ) : (
          filtered.map((e) => <EventCard key={e.message_id} event={e} />)
        )}
      </div>
    </div>
  );
}
