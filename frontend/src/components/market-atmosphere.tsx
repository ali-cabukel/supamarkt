"use client";

/** Decorative candlestick / grid atmosphere for the landing hero. */
export function MarketAtmosphere() {
  const candles = [
    { x: 40, o: 120, c: 70, h: 55, l: 140 },
    { x: 70, o: 80, c: 110, h: 65, l: 125 },
    { x: 100, o: 105, c: 60, h: 45, l: 118 },
    { x: 130, o: 70, c: 95, h: 55, l: 110 },
    { x: 160, o: 90, c: 50, h: 40, l: 105 },
    { x: 190, o: 55, c: 85, h: 42, l: 100 },
    { x: 220, o: 80, c: 45, h: 35, l: 95 },
    { x: 250, o: 50, c: 75, h: 40, l: 90 },
    { x: 280, o: 70, c: 40, h: 30, l: 85 },
    { x: 310, o: 45, c: 68, h: 35, l: 80 },
    { x: 340, o: 65, c: 35, h: 28, l: 78 },
    { x: 370, o: 40, c: 55, h: 30, l: 70 },
  ];

  return (
    <div
      className="pointer-events-none absolute inset-y-0 right-0 hidden w-[55%] opacity-40 lg:block"
      aria-hidden
    >
      <svg
        viewBox="0 0 420 180"
        className="absolute inset-0 h-full w-full text-accent"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          <linearGradient id="atm-fade" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#050807" stopOpacity="1" />
            <stop offset="35%" stopColor="#050807" stopOpacity="0" />
          </linearGradient>
        </defs>
        {candles.map((c, i) => {
          const up = c.c < c.o;
          const bodyTop = Math.min(c.o, c.c);
          const bodyH = Math.abs(c.o - c.c) || 2;
          return (
            <g key={i} className="animate-fade-up" style={{ animationDelay: `${0.05 * i}s` }}>
              <line
                x1={c.x}
                y1={c.h}
                x2={c.x}
                y2={c.l}
                stroke="currentColor"
                strokeWidth="1.5"
                opacity={up ? 0.7 : 0.35}
              />
              <rect
                x={c.x - 6}
                y={bodyTop}
                width="12"
                height={bodyH}
                fill="currentColor"
                opacity={up ? 0.85 : 0.25}
                rx="1"
              />
            </g>
          );
        })}
        <rect width="420" height="180" fill="url(#atm-fade)" />
      </svg>
    </div>
  );
}
