"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/protected-route";
import * as api from "@/lib/api";
import type { Instrument } from "@/lib/types";
import { ApiError } from "@/lib/types";

const REGIONS = ["", "US", "UK", "EU"] as const;

export default function InstrumentsPage() {
  return (
    <ProtectedRoute>
      <InstrumentsContent />
    </ProtectedRoute>
  );
}

function InstrumentsContent() {
  const [items, setItems] = useState<Instrument[]>([]);
  const [region, setRegion] = useState("");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listInstruments({
        region: region || undefined,
        q: query || undefined,
        limit: 100,
      });
      setItems(data.items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load instruments");
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [region, query]);

  useEffect(() => {
    const t = setTimeout(() => void load(), query ? 200 : 0);
    return () => clearTimeout(t);
  }, [load, query]);

  return (
    <main className="bg-market-soft mx-auto w-full max-w-6xl flex-1 px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Instruments</h1>
      <p className="mt-1 text-sm text-muted">Tracked symbols across US, UK, and EU exchanges.</p>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <input
          type="search"
          placeholder="Search symbol or name…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="field flex-1"
          aria-label="Search instruments"
        />
        <div className="flex flex-wrap gap-2">
          {REGIONS.map((r) => {
            const active = region === r;
            return (
              <button
                key={r || "all"}
                type="button"
                onClick={() => setRegion(r)}
                className={`chip text-sm ${active ? "chip-active" : ""}`}
              >
                {r || "All"}
              </button>
            );
          })}
        </div>
      </div>

      {loading && (
        <div className="mt-8 space-y-2" aria-busy>
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className="h-14 animate-pulse rounded-lg bg-surface-2"
              style={{ opacity: 1 - i * 0.1 }}
            />
          ))}
        </div>
      )}

      {error && (
        <div className="mt-8 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="mt-10 rounded-xl border border-dashed border-border bg-surface/40 px-6 py-12 text-center">
          <p className="font-medium">No instruments found</p>
          <p className="mt-1 text-sm text-muted">Try another search or region filter.</p>
        </div>
      )}

      {!loading && !error && items.length > 0 && (
        <ul className="mt-6 divide-y divide-border overflow-hidden rounded-xl border border-border">
          {items.map((item) => (
            <li key={item.id}>
              <Link
                href={`/instruments/${item.id}`}
                className="flex items-center justify-between gap-4 px-4 py-3.5 transition-colors hover:bg-accent-soft/50"
              >
                <div className="min-w-0">
                  <div className="flex items-baseline gap-2">
                    <span className="font-semibold tracking-tight">{item.symbol}</span>
                    <span className="font-mono text-xs text-muted">{item.mic}</span>
                  </div>
                  <p className="truncate text-sm text-muted">{item.name}</p>
                </div>
                <span className="shrink-0 rounded-md bg-surface-2 px-2 py-0.5 font-mono text-[11px] text-muted">
                  {item.region}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
