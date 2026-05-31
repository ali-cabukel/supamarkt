"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { PriceSparkline } from "@/components/price-sparkline";
import { ProtectedRoute } from "@/components/protected-route";
import * as api from "@/lib/api";
import type { PaginatedBars } from "@/lib/types";
import { ApiError } from "@/lib/types";

export default function InstrumentDetailPage() {
  return (
    <ProtectedRoute>
      <InstrumentDetailContent />
    </ProtectedRoute>
  );
}

function InstrumentDetailContent() {
  const params = useParams();
  const id = Number(params.id);
  const [data, setData] = useState<PaginatedBars | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!Number.isFinite(id)) return;
    setLoading(true);
    setError(null);
    try {
      setData(await api.getInstrumentBars(id, 120));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load bars");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-8">
      <Link href="/instruments" className="text-sm text-emerald-700 hover:underline dark:text-emerald-400">
        ← Instruments
      </Link>

      {loading && <p className="mt-8 text-zinc-500">Loading chart…</p>}
      {error && <p className="mt-8 text-sm text-red-600">{error}</p>}

      {data && (
        <>
          <h1 className="mt-4 text-2xl font-semibold">
            {data.symbol}
            <span className="ml-2 text-base font-normal text-zinc-500">{data.mic}</span>
          </h1>
          <p className="text-sm text-zinc-500">{data.interval} bars</p>
          <div className="mt-8 rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
            <PriceSparkline bars={data.items} />
          </div>
          {data.items.length > 0 && (
            <div className="mt-8 overflow-x-auto text-xs font-mono">
              <table className="min-w-full">
                <thead>
                  <tr className="text-left text-zinc-500">
                    <th className="py-1 pr-4">Time</th>
                    <th className="py-1 pr-4">O</th>
                    <th className="py-1 pr-4">H</th>
                    <th className="py-1 pr-4">L</th>
                    <th className="py-1 pr-4">C</th>
                    <th className="py-1">Vol</th>
                  </tr>
                </thead>
                <tbody>
                  {[...data.items].reverse().slice(0, 15).map((bar) => (
                    <tr key={bar.bar_ts} className="border-t border-zinc-100 dark:border-zinc-800">
                      <td className="py-1 pr-4">{bar.bar_ts}</td>
                      <td className="py-1 pr-4">{bar.open.toFixed(2)}</td>
                      <td className="py-1 pr-4">{bar.high.toFixed(2)}</td>
                      <td className="py-1 pr-4">{bar.low.toFixed(2)}</td>
                      <td className="py-1 pr-4">{bar.close.toFixed(2)}</td>
                      <td className="py-1">{bar.volume.toFixed(0)}</td>
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
