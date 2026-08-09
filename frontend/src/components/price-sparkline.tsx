import type { PriceBar } from "@/lib/types";

export function PriceSparkline({ bars }: { bars: PriceBar[] }) {
  if (bars.length < 2) {
    return <p className="text-sm text-muted">Not enough bars to chart.</p>;
  }

  const closes = bars.map((b) => b.close);
  const min = Math.min(...closes);
  const max = Math.max(...closes);
  const range = max - min || 1;
  const width = 480;
  const height = 120;
  const padding = 6;

  const coords = closes.map((close, i) => {
    const x = padding + (i / (closes.length - 1)) * (width - padding * 2);
    const y = padding + (1 - (close - min) / range) * (height - padding * 2);
    return { x, y };
  });

  const points = coords.map(({ x, y }) => `${x},${y}`).join(" ");
  const area = `${padding},${height - padding} ${points} ${width - padding},${height - padding}`;

  const last = closes[closes.length - 1];
  const first = closes[0];
  const change = ((last - first) / first) * 100;
  const up = change >= 0;

  return (
    <div>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full text-accent" role="img">
        <title>Price sparkline</title>
        <defs>
          <linearGradient id="spark-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="currentColor" stopOpacity="0.25" />
            <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
          </linearGradient>
        </defs>
        <polygon fill="url(#spark-fill)" points={area} />
        <polyline
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
          strokeLinecap="round"
          points={points}
        />
      </svg>
      <p className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
        <span>
          {bars.length} bars · last{" "}
          <span className="font-mono text-foreground">{last.toFixed(2)}</span>
        </span>
        <span className={`font-mono font-medium ${up ? "text-accent" : "text-danger"}`}>
          {up ? "+" : ""}
          {change.toFixed(2)}%
        </span>
      </p>
    </div>
  );
}
