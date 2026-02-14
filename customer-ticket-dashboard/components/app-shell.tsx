"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, MessageSquare } from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/", label: "Dashboard", icon: BarChart3 },
  { href: "/tickets", label: "Tickets", icon: MessageSquare },
] as const

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-background">
      {/* ── Floating top nav ──────────────────────────────── */}
      <header className="sticky top-0 z-50 w-full">
        <div className="mx-auto max-w-6xl px-6 pt-4">
          <nav className="flex items-center justify-between rounded-2xl bg-card/80 backdrop-blur-xl border border-border/40 shadow-[0_1px_3px_0_rgba(0,0,0,0.04),0_1px_2px_-1px_rgba(0,0,0,0.04)] px-5 h-14">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground transition-transform group-hover:scale-105">
                <span className="text-[10px] font-bold tracking-tight">DL</span>
              </div>
              <span className="text-sm font-semibold text-foreground tracking-tight">
                Daylight
              </span>
            </Link>

            {/* Nav pills */}
            <div className="flex items-center gap-0.5 rounded-xl bg-secondary/50 p-1">
              {navItems.map(({ href, label, icon: Icon }) => {
                const isActive =
                  href === "/" ? pathname === "/" : pathname.startsWith(href)
                return (
                  <Link
                    key={href}
                    href={href}
                    className={cn(
                      "flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-200",
                      isActive
                        ? "bg-card text-foreground shadow-sm"
                        : "text-muted-foreground hover:text-foreground"
                    )}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {label}
                  </Link>
                )
              })}
            </div>
          </nav>
        </div>
      </header>

      {/* ── Page content ──────────────────────────────────── */}
      <main className="mx-auto max-w-6xl px-6 py-6">{children}</main>
    </div>
  )
}
