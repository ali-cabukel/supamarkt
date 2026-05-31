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
    void load();
  }, [load]);

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Instruments</h1>
      <p className="mt-1 text-sm text-zinc-500">Tracked symbols across US, UK, and EU exchanges.</p>

      <div className="mt-6 flex flex-wrap gap-3">
        <input
          type="search"
          placeholder="Search symbol or name…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="min-w-[200px] flex-1 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-950"
        />
        <select
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-950"
        >
          {REGIONS.map((r) => (
            <option key={r || "all"} value={r}>
              {r || "All regions"}
            </option>
          ))}
        </select>
      </div>

      {loading && <p className="mt-8 text-zinc-500">Loading…</p>}
      {error && <p className="mt-8 text-sm text-red-600">{error}</p>}

      {!loading && !error && (
        <ul className="mt-6 divide-y divide-zinc-200 rounded-lg border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
          {items.map((item) => (
            <li key={item.id}>
              <Link
                href={`/instruments/${item.id}`}
                className="flex items-center justify-between px-4 py-3 hover:bg-zinc-50 dark:hover:bg-zinc-900/50"
              >
                <div>
                  <span className="font-medium">{item.symbol}</span>
                  <span className="ml-2 text-zinc-500">{item.mic}</span>
                  <p className="text-sm text-zinc-500">{item.name}</p>
                </div>
                <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs dark:bg-zinc-800">
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
