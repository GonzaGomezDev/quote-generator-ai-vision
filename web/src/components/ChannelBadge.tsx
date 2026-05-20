interface Props {
  channel: "whatsapp" | "instagram";
}

const styles: Record<string, string> = {
  whatsapp: "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400",
  instagram: "bg-pink-50 text-pink-700 dark:bg-pink-500/10 dark:text-pink-400",
};

const icons: Record<string, string> = {
  whatsapp: "💬",
  instagram: "📸",
};

export function ChannelBadge({ channel }: Props) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${styles[channel]}`}>
      {icons[channel]} {channel}
    </span>
  );
}
