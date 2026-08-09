"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { ProtectedRoute } from "@/components/protected-route";
import { SignalBadge } from "@/components/signal-badge";
import * as api from "@/lib/api";
import type { Signal } from "@/lib/types";
import { ApiError } from "@/lib/types";

type ActionFilter = "ALL" | "BUY" | "SELL" | "HOLD";

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
  const [actionFilter, setActionFilter] = useState<ActionFilter>("ALL");
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

  const filtered = useMemo(() => {
    if (actionFilter === "ALL") return signals;
    return signals.filter((s) => s.action === actionFilter);
  }, [signals, actionFilter]);

  const counts = useMemo(() => {
    const base = { BUY: 0, SELL: 0, HOLD: 0 };
    for (const s of signals) {
      if (s.action in base) base[s.action as keyof typeof base] += 1;
    }
    return base;
  }, [signals]);

  return (
    <main className="bg-market-soft mx-auto w-full max-w-6xl flex-1 px-4 py-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Signals</h1>
          <p className="mt-1 text-sm text-muted">
            Latest buy / hold / sell from stored 5m bars.
          </p>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          <label className="text-sm">
            <span className="mb-1.5 block text-xs text-muted">Watchlist</span>
            <select
              value={watchlist}
              onChange={(e) => setWatchlist(e.target.value)}
              className="field !w-auto min-w-[11rem]"
            >
              <option value="default">default (US + UK + EU)</option>
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1.5 block text-xs text-muted">Strategy</span>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="field !w-auto min-w-[10rem]"
            >
              <option value="ema_trend_5m">ema_trend_5m</option>
            </select>
          </label>
          <button type="button" onClick={() => void load()} className="btn-ghost !py-2.5 text-sm">
            Refresh
          </button>
        </div>
      </div>

      {disclaimer && (
        <p className="mt-5 rounded-lg border border-warn/25 bg-warn/10 px-3.5 py-2.5 text-sm text-warn">
          {disclaimer}
        </p>
      )}

      {!loading && signals.length > 0 && (
        <div className="mt-5 flex flex-wrap gap-2">
          {(
            [
              ["ALL", signals.length],
              ["BUY", counts.BUY],
              ["SELL", counts.SELL],
              ["HOLD", counts.HOLD],
            ] as const
          ).map(([key, count]) => {
            const active = actionFilter === key;
            return (
              <button
                key={key}
                type="button"
                onClick={() => setActionFilter(key)}
                className={`chip font-mono ${active ? "chip-active" : ""}`}
              >
                {key} · {count}
              </button>
            );
          })}
        </div>
      )}

      {loading && (
        <div className="mt-8 space-y-2" aria-busy>
          {[0, 1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-12 animate-pulse rounded-lg bg-surface-2"
              style={{ opacity: 1 - i * 0.12 }}
            />
          ))}
        </div>
      )}

      {error && (
        <div className="mt-8 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      {!loading && !error && signals.length === 0 && (
        <div className="mt-10 rounded-xl border border-dashed border-border bg-surface/40 px-6 py-12 text-center">
          <p className="text-base font-medium">No signals yet</p>
          <p className="mx-auto mt-2 max-w-md text-sm text-muted">
            Collect bars and run analysis in the backend, then hit Refresh.
          </p>
          <pre className="mx-auto mt-5 max-w-lg overflow-x-auto rounded-lg border border-border bg-background px-4 py-3 text-left font-mono text-xs text-accent">
            {`supamarkt collect-intraday --watchlist default
supamarkt analyze --watchlist default --strategy ema_trend_5m`}
          </pre>
        </div>
      )}

      {!loading && filtered.length > 0 && (
        <div className="mt-6 overflow-x-auto rounded-xl border border-border">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-border bg-surface-2/80 text-xs uppercase tracking-wider text-muted">
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
              {filtered.map((signal) => (
                <tr
                  key={signal.id}
                  className="border-b border-border/70 last:border-0 hover:bg-accent-soft/40"
                >
                  <td className="px-4 py-3">
                    <Link
                      href={`/instruments/${signal.instrument_id}`}
                      className="font-medium text-accent hover:underline"
                    >
                      {signal.symbol}
                    </Link>
                    <span className="ml-1.5 font-mono text-xs text-muted">{signal.mic}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded px-1.5 py-0.5 font-mono text-[11px] text-muted bg-surface-2">
                      {signal.region}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <SignalBadge action={signal.action} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-surface-2">
                        <div
                          className="h-full rounded-full bg-accent"
                          style={{ width: `${Math.round(signal.confidence * 100)}%` }}
                        />
                      </div>
                      <span className="font-mono text-xs tabular-nums">
                        {(signal.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-muted">{signal.bar_ts}</td>
                  <td className="max-w-xs px-4 py-3 text-xs text-muted">
                    <ul className="list-disc space-y-0.5 pl-4">
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

      {!loading && signals.length > 0 && filtered.length === 0 && (
        <p className="mt-8 text-sm text-muted">No signals match this filter.</p>
      )}
    </main>
  );
}
