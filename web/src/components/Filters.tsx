import type { ChannelFilter, MatchFilter } from "../lib/types";

interface Props {
  channel: ChannelFilter;
  match: MatchFilter;
  onChannel: (v: ChannelFilter) => void;
  onMatch: (v: MatchFilter) => void;
  total: number;
}

function Pill({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
        active
          ? "bg-brand-500 text-white"
          : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700"
      }`}
    >
      {children}
    </button>
  );
}

export function Filters({ channel, match, onChannel, onMatch, total }: Props) {
  return (
    <div className="flex items-center gap-3 flex-wrap">
      <span className="text-sm text-gray-500 dark:text-gray-400">{total} eventos</span>
      <div className="flex gap-1">
        {([["all", "todos"], ["whatsapp", "WhatsApp"], ["messenger", "Messenger"]] as [ChannelFilter, string][]).map(([v, label]) => (
          <Pill key={v} active={channel === v} onClick={() => onChannel(v)}>
            {label}
          </Pill>
        ))}
      </div>
      <div className="flex gap-1">
        {([["all", "todos"], ["matched", "con cotización"], ["unmatched", "sin cotización"]] as [MatchFilter, string][]).map(([v, label]) => (
          <Pill key={v} active={match === v} onClick={() => onMatch(v)}>
            {label}
          </Pill>
        ))}
      </div>
    </div>
  );
}
