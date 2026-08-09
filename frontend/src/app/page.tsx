"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { LogoMark } from "@/components/logo-mark";
import { MarketAtmosphere } from "@/components/market-atmosphere";
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
      <div className="flex flex-1 items-center justify-center py-24 text-muted">Loading…</div>
    );
  }

  return (
    <main className="bg-market relative flex flex-1 flex-col overflow-hidden">
      {/* Atmospheric scan line / glow accents */}
      <div
        className="pointer-events-none absolute inset-x-0 top-24 h-px bg-gradient-to-r from-transparent via-accent/40 to-transparent animate-pulse-soft"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -right-24 top-1/3 h-72 w-72 rounded-full bg-accent/10 blur-3xl"
        aria-hidden
      />
      <MarketAtmosphere />

      <div className="relative mx-auto flex w-full max-w-5xl flex-1 flex-col justify-center px-4 py-16 sm:py-24">
        <div className="animate-fade-up flex items-center gap-3">
          <LogoMark className="h-10 w-10 sm:h-12 sm:w-12" />
          <p className="font-mono text-xs font-medium uppercase tracking-[0.2em] text-accent">
            US · UK · EU
          </p>
        </div>

        <h1 className="animate-fade-up-delay mt-6 text-5xl font-bold tracking-tight sm:text-7xl md:text-8xl">
          supamarkt
        </h1>

        <p className="animate-fade-up-delay-2 mt-5 max-w-xl text-lg text-muted sm:text-xl">
          Intraday bars and rule-based buy / hold / sell signals — a research terminal, not
          investment advice.
        </p>

        <div className="animate-fade-up-delay-2 mt-10 flex flex-wrap gap-3">
          <Link href="/login" className="btn-primary">
            Log in
          </Link>
          <Link href="/register" className="btn-ghost">
            Create account
          </Link>
        </div>
      </div>
    </main>
  );
}
