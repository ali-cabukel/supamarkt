"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";

import { LogoMark } from "@/components/logo-mark";
import { useAuth } from "@/contexts/auth-context";
import { ApiError } from "@/lib/types";

export default function RegisterPage() {
  const { user, loading, register } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && user) router.replace("/signals");
  }, [loading, user, router]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(email, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading || user) {
    return (
      <div className="flex flex-1 items-center justify-center py-24 text-muted">Loading…</div>
    );
  }

  return (
    <main className="bg-market-soft flex flex-1 flex-col justify-center px-4 py-12">
      <div className="mx-auto w-full max-w-md">
        <div className="mb-8 flex items-center gap-2.5">
          <LogoMark className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Create account</h1>
            <p className="text-sm text-muted">Start exploring market signals.</p>
          </div>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-4 rounded-xl border border-border bg-surface/80 p-6 backdrop-blur"
        >
          <label className="block text-sm">
            <span className="mb-1.5 block text-muted">Email</span>
            <input
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="field"
              placeholder="you@example.com"
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1.5 block text-muted">Password</span>
            <input
              type="password"
              required
              minLength={8}
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="field"
              placeholder="At least 8 characters"
            />
          </label>
          {error && (
            <p className="rounded-md border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-danger">
              {error}
            </p>
          )}
          <button type="submit" disabled={submitting} className="btn-primary w-full">
            {submitting ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-accent hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </main>
  );
}
