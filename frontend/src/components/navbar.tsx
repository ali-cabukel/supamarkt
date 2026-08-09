"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { LogoMark } from "@/components/logo-mark";
import { useAuth } from "@/contexts/auth-context";

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  const pathname = usePathname();
  const active = pathname === href || pathname.startsWith(`${href}/`);

  return (
    <Link
      href={href}
      className={`rounded-md px-2.5 py-1.5 transition-colors ${
        active
          ? "bg-accent text-accent-on font-semibold shadow-[0_0_12px_rgba(34,197,94,0.35)]"
          : "text-muted hover:text-foreground"
      }`}
    >
      {children}
    </Link>
  );
}

export function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/85 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4">
        <Link
          href={user ? "/signals" : "/"}
          className="group flex items-center gap-2.5"
        >
          <LogoMark className="h-7 w-7 transition-transform group-hover:scale-105" />
          <span className="text-base font-semibold tracking-tight">supamarkt</span>
        </Link>

        <nav className="flex items-center gap-1 text-sm sm:gap-2">
          {user ? (
            <>
              <NavLink href="/signals">Signals</NavLink>
              <NavLink href="/instruments">Instruments</NavLink>
              <span className="mx-1 hidden max-w-[160px] truncate text-xs text-muted md:inline">
                {user.email}
              </span>
              <button type="button" onClick={logout} className="btn-ghost !px-3 !py-1.5 text-xs">
                Log out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="px-2.5 py-1.5 text-muted hover:text-foreground">
                Log in
              </Link>
              <Link href="/register" className="btn-primary !px-3 !py-1.5 text-xs">
                Register
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
