"use client";

import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { PriceSparkline } from "@/components/price-sparkline";
import { ProtectedRoute } from "@/components/protected-route";
import * as api from "@/lib/api";
import { resolveInstrumentId } from "@/lib/instrument-path";
import type { PaginatedBars } from "@/lib/types";
import { ApiError } from "@/lib/types";

export function InstrumentDetailPage() {
  return (
    <ProtectedRoute>
      <InstrumentDetailContent />
    </ProtectedRoute>
  );
}

function InstrumentDetailContent() {
  const pathname = usePathname();
  const params = useParams<{ id: string }>();
  const [instrumentId, setInstrumentId] = useState<number | null>(() =>
    resolveInstrumentId(pathname, params.id),
  );
  const [data, setData] = useState<PaginatedBars | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setInstrumentId(resolveInstrumentId(pathname, params.id));
  }, [pathname, params.id]);

  const load = useCallback(async () => {
    if (instrumentId === null) return;
    setLoading(true);
    setError(null);
    try {
      setData(await api.getInstrumentBars(instrumentId, 120));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load bars");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [instrumentId]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <main className="bg-market-soft mx-auto w-full max-w-3xl flex-1 px-4 py-8">
      <Link
        href="/instruments"
        className="inline-flex items-center gap-1 text-sm text-accent hover:underline"
      >
        ← Instruments
      </Link>

      {loading && (
        <div className="mt-8 space-y-3" aria-busy>
          <div className="h-8 w-40 animate-pulse rounded bg-surface-2" />
          <div className="h-40 animate-pulse rounded-xl bg-surface-2" />
        </div>
      )}

      {error && (
        <div className="mt-8 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      {data && (
        <>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight">
            {data.symbol}
            <span className="ml-2 font-mono text-base font-normal text-muted">{data.mic}</span>
          </h1>
          <p className="mt-1 text-sm text-muted">{data.interval} bars</p>

          <div className="mt-8 rounded-xl border border-border bg-surface/60 p-5">
            <PriceSparkline bars={data.items} />
          </div>

          {data.items.length > 0 && (
            <div className="mt-8 overflow-x-auto rounded-xl border border-border">
              <table className="min-w-full font-mono text-xs">
                <thead className="border-b border-border bg-surface-2/80 text-left text-muted">
                  <tr>
                    <th className="px-3 py-2 font-medium">Time</th>
                    <th className="px-3 py-2 font-medium">O</th>
                    <th className="px-3 py-2 font-medium">H</th>
                    <th className="px-3 py-2 font-medium">L</th>
                    <th className="px-3 py-2 font-medium">C</th>
                    <th className="px-3 py-2 font-medium">Vol</th>
                  </tr>
                </thead>
                <tbody>
                  {[...data.items]
                    .reverse()
                    .slice(0, 15)
                    .map((bar) => (
                      <tr
                        key={bar.bar_ts}
                        className="border-t border-border/70 hover:bg-accent-soft/30"
                      >
                        <td className="px-3 py-1.5 text-muted">{bar.bar_ts}</td>
                        <td className="px-3 py-1.5 tabular-nums">{bar.open.toFixed(2)}</td>
                        <td className="px-3 py-1.5 tabular-nums">{bar.high.toFixed(2)}</td>
                        <td className="px-3 py-1.5 tabular-nums">{bar.low.toFixed(2)}</td>
                        <td className="px-3 py-1.5 tabular-nums text-accent">
                          {bar.close.toFixed(2)}
                        </td>
                        <td className="px-3 py-1.5 tabular-nums text-muted">
                          {bar.volume.toFixed(0)}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </main>
  );
}
