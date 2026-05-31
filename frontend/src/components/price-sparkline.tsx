import type { PriceBar } from "@/lib/types";

export function PriceSparkline({ bars }: { bars: PriceBar[] }) {
  if (bars.length < 2) {
    return <p className="text-sm text-zinc-500">Not enough bars to chart.</p>;
  }

  const closes = bars.map((b) => b.close);
  const min = Math.min(...closes);
  const max = Math.max(...closes);
  const range = max - min || 1;
  const width = 320;
  const height = 80;
  const padding = 4;

  const points = closes
    .map((close, i) => {
      const x = padding + (i / (closes.length - 1)) * (width - padding * 2);
      const y = padding + (1 - (close - min) / range) * (height - padding * 2);
      return `${x},${y}`;
    })
    .join(" ");

  const last = closes[closes.length - 1];
  const first = closes[0];
  const change = ((last - first) / first) * 100;

  return (
    <div>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full max-w-md text-emerald-600">
        <polyline
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
          points={points}
        />
      </svg>
      <p className="mt-2 text-sm text-zinc-500">
        {bars.length} bars · last {last.toFixed(2)} ·{" "}
        <span className={change >= 0 ? "text-emerald-600" : "text-red-600"}>
          {change >= 0 ? "+" : ""}
          {change.toFixed(2)}%
        </span>
      </p>
    </div>
  );
}
