const STYLES: Record<string, string> = {
  BUY: "bg-emerald-100 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-300",
  SELL: "bg-red-100 text-red-900 dark:bg-red-950 dark:text-red-300",
  HOLD: "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300",
};

export function SignalBadge({ action }: { action: string }) {
  const style = STYLES[action] ?? STYLES.HOLD;
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ${style}`}>
      {action}
    </span>
  );
}
