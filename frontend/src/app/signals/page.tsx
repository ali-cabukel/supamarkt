"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/protected-route";
import { SignalBadge } from "@/components/signal-badge";
import * as api from "@/lib/api";
import type { Signal } from "@/lib/types";
import { ApiError } from "@/lib/types";

export default function SignalsPage() {
  return (
    <ProtectedRoute>
      <SignalsContent />
    </ProtectedRoute>
  );
}

function SignalsContent() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [disclaimer, setDisclaimer] = useState<string>("");
  const [watchlist, setWatchlist] = useState("default");
  const [strategy, setStrategy] = useState("ema_trend_5m");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listSignals({
        watchlist,
        strategy,
        limit: 50,
      });
      setSignals(data.items);
      setDisclaimer(data.items[0]?.disclaimer ?? "");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load signals");
      setSignals([]);
    } finally {
      setLoading(false);
    }
  }, [watchlist, strategy]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Signals</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Latest buy / hold / sell from stored 5m bars.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <label className="text-sm">
            <span className="mb-1 block text-zinc-500">Watchlist</span>
            <select
              value={watchlist}
              onChange={(e) => setWatchlist(e.target.value)}
              className="rounded-md border border-zinc-300 bg-white px-3 py-2 dark:border-zinc-700 dark:bg-zinc-950"
            >
              <option value="default">default (US + UK + EU)</option>
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-zinc-500">Strategy</span>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="rounded-md border border-zinc-300 bg-white px-3 py-2 dark:border-zinc-700 dark:bg-zinc-950"
            >
              <option value="ema_trend_5m">ema_trend_5m</option>
            </select>
          </label>
          <button
            type="button"
            onClick={() => void load()}
            className="self-end rounded-md border border-zinc-300 px-4 py-2 text-sm hover:bg-zinc-50 dark:border-zinc-700 dark:hover:bg-zinc-900"
          >
            Refresh
          </button>
        </div>
      </div>

      {disclaimer && (
        <p className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-200">
          {disclaimer}
        </p>
      )}

      {loading && <p className="mt-8 text-zinc-500">Loading signals…</p>}
      {error && <p className="mt-8 text-sm text-red-600 dark:text-red-400">{error}</p>}

      {!loading && !error && signals.length === 0 && (
        <p className="mt-8 text-zinc-500">
          No signals yet. Run{" "}
          <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-800">supamarkt collect-intraday</code>{" "}
          and{" "}
          <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-800">supamarkt analyze</code> in the
          backend.
        </p>
      )}

      {!loading && signals.length > 0 && (
        <div className="mt-6 overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900/50">
              <tr>
                <th className="px-4 py-3 font-medium">Symbol</th>
                <th className="px-4 py-3 font-medium">Region</th>
                <th className="px-4 py-3 font-medium">Action</th>
                <th className="px-4 py-3 font-medium">Confidence</th>
                <th className="px-4 py-3 font-medium">Bar</th>
                <th className="px-4 py-3 font-medium">Reasons</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((signal) => (
                <tr
                  key={signal.id}
                  className="border-b border-zinc-100 last:border-0 dark:border-zinc-800/80"
                >
                  <td className="px-4 py-3">
                    <Link
                      href={`/instruments/${signal.instrument_id}`}
                      className="font-medium text-emerald-700 hover:underline dark:text-emerald-400"
                    >
                      {signal.symbol}
                    </Link>
                    <span className="ml-1 text-zinc-500">{signal.mic}</span>
                  </td>
                  <td className="px-4 py-3">{signal.region}</td>
                  <td className="px-4 py-3">
                    <SignalBadge action={signal.action} />
                  </td>
                  <td className="px-4 py-3">{(signal.confidence * 100).toFixed(0)}%</td>
                  <td className="px-4 py-3 font-mono text-xs">{signal.bar_ts}</td>
                  <td className="max-w-xs px-4 py-3 text-xs text-zinc-600 dark:text-zinc-400">
                    <ul className="list-disc pl-4">
                      {signal.reasons.map((r) => (
                        <li key={r}>{r}</li>
                      ))}
                    </ul>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
