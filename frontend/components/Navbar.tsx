"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { Waves, LogOut } from "lucide-react";
import ThemeToggle from "@/components/ThemeToggle";
import { useAuth } from "@/components/providers/AuthProvider";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/pump", label: "3D Pump" },
  { href: "/trends", label: "Trends" },
];

export default function Navbar() {
  const pathname = usePathname();
  const { isAuthenticated, logout } = useAuth();

  if (pathname === "/login") return null;

  return (
    <header className="border-b border-border">
      <nav className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2 shrink-0">
            <Waves size={20} className="text-accent" />
            <span className="font-semibold tracking-tight hidden sm:inline">
              Digital Twin
            </span>
          </Link>
          <div className="flex items-center gap-1">
            {LINKS.map((link) => {
              const active = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={clsx(
                    "px-3 py-1.5 rounded-full text-sm transition-colors",
                    active
                      ? "bg-surface-hover text-foreground"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          {isAuthenticated && (
            <button
              onClick={logout}
              className="w-9 h-9 rounded-full flex items-center justify-center border border-border text-muted-foreground hover:text-risk-critical hover:bg-surface-hover transition-colors"
              title="Log out"
              aria-label="Log out"
            >
              <LogOut size={16} />
            </button>
          )}
        </div>
      </nav>
    </header>
  );
}
