"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/contexts/auth-context";

export default function HomePage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.replace("/signals");
    }
  }, [loading, user, router]);

  if (loading || user) {
    return (
      <div className="flex flex-1 items-center justify-center py-24 text-zinc-500">Loading…</div>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center px-4 py-16">
      <p className="text-sm font-medium uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
        US · UK · EU
      </p>
      <h1 className="mt-2 text-4xl font-semibold tracking-tight">supamarkt</h1>
      <p className="mt-4 text-lg text-zinc-600 dark:text-zinc-400">
        Intraday market data and rule-based buy / hold / sell signals. Research tool only — not
        investment advice.
      </p>
      <div className="mt-8 flex flex-wrap gap-3">
        <Link
          href="/login"
          className="rounded-md bg-emerald-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-emerald-600"
        >
          Log in
        </Link>
        <Link
          href="/register"
          className="rounded-md border border-zinc-300 px-5 py-2.5 text-sm font-medium hover:bg-zinc-50 dark:border-zinc-700 dark:hover:bg-zinc-900"
        >
          Create account
        </Link>
      </div>
      <p className="mt-10 text-sm text-zinc-500">
        Backend: run <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-800">supamarkt-api</code>{" "}
        on port 8000, then collect and analyze via CLI.
      </p>
    </main>
  );
}
