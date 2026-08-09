const STYLES: Record<string, string> = {
  BUY: "bg-accent/20 text-accent",
  SELL: "bg-red-500/15 text-danger",
  HOLD: "bg-zinc-500/15 text-muted",
};

export function SignalBadge({ action }: { action: string }) {
  const style = STYLES[action] ?? STYLES.HOLD;
  return (
    <span
      className={`inline-flex min-w-[3.5rem] items-center justify-center rounded-md px-2 py-0.5 font-mono text-[11px] font-semibold tracking-wide ${style}`}
    >
      {action}
    </span>
  );
}
