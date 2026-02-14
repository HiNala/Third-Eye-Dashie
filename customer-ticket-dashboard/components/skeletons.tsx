import React from "react"
import { cn } from "@/lib/utils"

function Bone({ className, style }: { className?: string; style?: React.CSSProperties }) {
  return <div className={cn("rounded-lg bg-muted/70 animate-pulse", className)} style={style} />
}

/* ── Dashboard skeleton ──────────────────────────────────────── */

export function DashboardSkeleton() {
  return (
    <div className="flex flex-col gap-5 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex items-baseline justify-between">
        <div>
          <Bone className="h-7 w-32" />
          <Bone className="h-4 w-44 mt-2" />
        </div>
        <Bone className="h-4 w-28" />
      </div>

      {/* At a Glance */}
      <div className="rounded-2xl bg-card border border-border/50 py-7 px-7">
        <div className="flex items-center gap-5 flex-wrap">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="flex items-center gap-2.5">
              <Bone className="h-9 w-9 rounded-lg" />
              <div>
                <Bone className="h-5 w-8" />
                <Bone className="h-3 w-16 mt-1" />
              </div>
            </div>
          ))}
          <div className="flex items-center gap-3 ml-auto">
            <Bone className="h-[72px] w-[72px] rounded-full" />
            <div className="flex flex-col gap-1">
              {[1, 2, 3, 4].map((i) => (
                <Bone key={i} className="h-2.5 w-20" />
              ))}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4 mt-5 pt-4 border-t border-border/30 flex-wrap">
          {/* AI Confidence */}
          <div className="flex items-center gap-2.5">
            <Bone className="h-3.5 w-3.5" />
            <Bone className="h-3 w-20" />
            <Bone className="h-1.5 w-24 rounded-full" />
            <Bone className="h-3 w-8" />
          </div>
          <Bone className="h-3 w-px" />
          {/* Resolution Rate */}
          <div className="flex items-center gap-2.5">
            <Bone className="h-3.5 w-3.5" />
            <Bone className="h-3 w-24" />
            <Bone className="h-1.5 w-24 rounded-full" />
            <Bone className="h-3 w-8" />
          </div>
          <Bone className="h-3 w-px" />
          {/* New today */}
          <div className="flex items-center gap-1.5">
            <Bone className="h-2 w-2 rounded-full" />
            <Bone className="h-3 w-16" />
          </div>
        </div>
      </div>

      {/* Three columns — uniform 4 rows each */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {[1, 2, 3].map((col) => (
          <div key={col} className="rounded-2xl bg-card border border-border/50 p-4 flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bone className="h-8 w-8 rounded-lg" />
                <Bone className="h-4 w-24" />
              </div>
              <Bone className="h-4 w-14" />
            </div>
            <div className="flex flex-col gap-1">
              {Array.from({ length: 4 }).map((_, j) => (
                <div key={j} className="flex items-start gap-3 px-3 py-2 rounded-lg border-l-[3px] border-l-muted">
                  <div className="flex-1">
                    <Bone className="h-4 w-full max-w-[220px]" />
                    <Bone className="h-3 w-28 mt-1" />
                  </div>
                  <Bone className="h-5 w-16 rounded-full" />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Bottom categories */}
      <div className="rounded-2xl bg-card border border-border/50 p-5">
        <Bone className="h-4 w-32 mb-1" />
        <Bone className="h-3 w-28 mb-4" />
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-7 gap-3">
          {[1, 2, 3, 4, 5, 6, 7].map((i) => (
            <div key={i} className="rounded-xl border border-border/40 p-4 flex flex-col items-center gap-2">
              <Bone className="h-4 w-20" />
              <Bone className="h-6 w-8" />
              <Bone className="h-2.5 w-full max-w-[100px]" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ── Tickets list skeleton ───────────────────────────────────── */

export function TicketsListSkeleton() {
  return (
    <div className="flex flex-col gap-5 animate-in fade-in duration-300">
      <div>
        <Bone className="h-6 w-28" />
        <Bone className="h-4 w-20 mt-2" />
      </div>
      <div className="rounded-2xl bg-card border border-border/50 overflow-hidden">
        {/* Filter bar */}
        <div className="flex items-center gap-2.5 px-5 py-2.5 border-b border-border/40 min-h-[48px]">
          <Bone className="h-8 w-56 rounded-lg" />
          <div className="h-5 w-px bg-border" />
          <Bone className="h-7 w-24 rounded-full" />
        </div>
        {/* Header */}
        <div className="flex items-center gap-3 px-5 py-2.5 border-b border-border/40">
          {[44, 0, 86, 86, 130, 76, 70, 48].map((w, i) => (
            <Bone key={i} className={cn("h-3", w ? `w-[${w}px] shrink-0` : "flex-1")} style={w ? { width: w } : undefined} />
          ))}
        </div>
        {/* Rows */}
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className={cn("flex items-center gap-3 px-5 py-3.5", i < 7 && "border-b border-border/20")}>
            <div className="w-[44px] shrink-0 flex items-center gap-1.5">
              <Bone className="h-2 w-2 rounded-full" />
              <Bone className="h-3 w-8" />
            </div>
            <div className="flex-1 min-w-0">
              <Bone className="h-4 w-full max-w-[320px]" />
              <Bone className="h-3 w-40 mt-1.5" />
            </div>
            <Bone className="h-[18px] w-16 rounded-full shrink-0" />
            <Bone className="h-[18px] w-16 rounded-full shrink-0" />
            <Bone className="h-[18px] w-14 rounded-full shrink-0" />
            <Bone className="h-1.5 w-10 rounded-full shrink-0" />
            <Bone className="h-[18px] w-14 rounded-full shrink-0" />
            <Bone className="h-3 w-8 shrink-0" />
          </div>
        ))}
      </div>
    </div>
  )
}

/* ── Ticket detail skeleton ──────────────────────────────────── */

export function TicketDetailSkeleton() {
  return (
    <div className="flex flex-col gap-5 animate-in fade-in duration-300">
      {/* Back link */}
      <Bone className="h-4 w-28" />

      {/* Header card */}
      <div className="rounded-2xl bg-card border border-border/50 overflow-hidden">
        <div className="px-6 py-5">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Bone className="h-[22px] w-10 rounded-full" />
                <Bone className="h-[22px] w-16 rounded-full" />
                <Bone className="h-[22px] w-14 rounded-full" />
              </div>
              <Bone className="h-5 w-72" />
            </div>
            <Bone className="h-7 w-16 rounded-full" />
          </div>
        </div>
        <div className="px-6 py-3 border-t border-border/30 bg-secondary/15 flex items-center gap-5">
          {[80, 140, 90, 60, 70].map((w, i) => (
            <div key={i} className="flex items-center gap-1.5">
              <Bone className="h-3.5 w-3.5 rounded" />
              <Bone className="h-3" style={{ width: w }} />
            </div>
          ))}
        </div>
      </div>

      {/* Content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-5">
        {/* Left column */}
        <div className="flex flex-col gap-5">
          {/* Customer message card */}
          <div className="rounded-2xl bg-card border border-border/50 overflow-hidden">
            <div className="px-6 py-3 border-b border-border/30 flex items-center gap-2">
              <Bone className="h-6 w-6 rounded-full" />
              <Bone className="h-3 w-24" />
              <Bone className="h-3 w-16 ml-auto" />
            </div>
            <div className="px-6 py-5 space-y-3">
              <Bone className="h-4 w-full" />
              <Bone className="h-4 w-[92%]" />
              <Bone className="h-4 w-[78%]" />
              <Bone className="h-4 w-full" />
              <Bone className="h-4 w-[65%]" />
            </div>
          </div>

          {/* Reply box card */}
          <div className="rounded-2xl bg-card border border-border/50 overflow-hidden">
            <div className="px-6 py-3 border-b border-border/30">
              <Bone className="h-3 w-28" />
            </div>
            <div className="p-4">
              <div className="rounded-2xl border border-border/40 p-2">
                <Bone className="h-[44px] w-full rounded-lg" />
                <div className="flex items-center justify-between pt-2 px-1">
                  <div className="flex items-center gap-1.5">
                    <Bone className="h-3 w-10" />
                    <Bone className="h-7 w-[120px] rounded-lg" />
                  </div>
                  <Bone className="h-8 w-8 rounded-full" />
                </div>
              </div>
            </div>
          </div>

          {/* Confidence strip */}
          <div className="rounded-2xl bg-card border border-border/50 px-6 py-4 flex items-center gap-4">
            <Bone className="h-3 w-20" />
            <Bone className="h-1.5 flex-1 max-w-[200px] rounded-full" />
            <Bone className="h-3 w-10" />
          </div>
        </div>

        {/* Right column — AI panel */}
        <div className="rounded-2xl bg-card border border-border/50 overflow-hidden">
          <div className="px-5 py-4 border-b border-border/40 flex items-center gap-2">
            <Bone className="h-4 w-4" />
            <Bone className="h-4 w-20" />
          </div>
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className={cn("px-5 py-4", i < 5 && "border-b border-border/30")}>
              <Bone className="h-2.5 w-16 mb-2" />
              <div className="flex items-center gap-2">
                <Bone className="h-6 w-16 rounded-full" />
                {i < 3 && <Bone className="h-6 w-14 rounded-full" />}
              </div>
              {i === 1 && <Bone className="h-1.5 w-full rounded-full mt-2" />}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
