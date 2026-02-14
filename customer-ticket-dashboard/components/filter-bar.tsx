"use client"

import { Search, X, Crown, SlidersHorizontal } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import type { TicketFilters, FilterKey } from "@/lib/filters"

/* ── config ──────────────────────────────────────────────────── */

interface FilterOption {
  value: string
  label: string
  dot?: string
}

interface FilterSection {
  key: FilterKey
  label: string
  options: FilterOption[]
}

const filterSections: FilterSection[] = [
  {
    key: "sentiment",
    label: "Sentiment",
    options: [
      { value: "positive", label: "Positive", dot: "bg-emerald-500" },
      { value: "negative", label: "Negative", dot: "bg-rose-500" },
      { value: "neutral", label: "Neutral", dot: "bg-amber-400" },
    ],
  },
  {
    key: "emotional_tone",
    label: "Emotion",
    options: [
      { value: "angry", label: "Angry", dot: "bg-rose-600" },
      { value: "frustrated", label: "Frustrated", dot: "bg-orange-500" },
      { value: "happy", label: "Happy", dot: "bg-amber-500" },
      { value: "delighted", label: "Delighted", dot: "bg-emerald-500" },
      { value: "neutral", label: "Neutral", dot: "bg-stone-400" },
    ],
  },
  {
    key: "status",
    label: "Status",
    options: [
      { value: "open", label: "Open", dot: "bg-amber-500" },
      { value: "in_progress", label: "In Progress", dot: "bg-sky-500" },
      { value: "closed", label: "Closed", dot: "bg-stone-400" },
    ],
  },
  {
    key: "priority",
    label: "Priority",
    options: [
      { value: "urgent", label: "Urgent", dot: "bg-red-500" },
      { value: "high", label: "High", dot: "bg-orange-500" },
      { value: "normal", label: "Normal", dot: "bg-amber-400" },
      { value: "low", label: "Low", dot: "bg-stone-300" },
    ],
  },
  {
    key: "topic",
    label: "Topic",
    options: [
      { value: "product", label: "Product" },
      { value: "shipping", label: "Shipping" },
      { value: "billing", label: "Billing" },
      { value: "returns", label: "Returns" },
      { value: "feature-request", label: "Feature Request" },
      { value: "warranty", label: "Warranty" },
      { value: "accessories", label: "Accessories" },
      { value: "company", label: "Company" },
    ],
  },
]

/* ── props ────────────────────────────────────────────────────── */

interface FilterBarProps {
  filters: TicketFilters
  onToggle: (key: FilterKey, value: string) => void
  onToggleVip: () => void
  onSearch: (value: string) => void
  onClearAll: () => void
}

/* ── component ───────────────────────────────────────────────── */

export function FilterBar({ filters, onToggle, onToggleVip, onSearch, onClearAll }: FilterBarProps) {
  const activeChips: { key: FilterKey; value: string; label: string }[] = []
  for (const section of filterSections) {
    const selected = filters[section.key] as string[]
    for (const opt of section.options) {
      if (selected.includes(opt.value)) {
        activeChips.push({ key: section.key, value: opt.value, label: `${section.label}: ${opt.label}` })
      }
    }
  }
  const hasVip = filters.vip === true
  const hasAny = activeChips.length > 0 || hasVip

  return (
    <div className="flex items-center gap-2.5 px-5 py-2.5 border-b border-border/30 min-h-[48px]">
      {/* Search */}
      <div className="relative w-56 shrink-0">
        <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground/60" />
        <Input
          placeholder="Search tickets..."
          value={filters.search}
          onChange={(e) => onSearch(e.target.value)}
          className="pl-9 h-8 text-xs bg-background/50 rounded-lg border-border/40 focus:border-primary/30 transition-colors"
        />
      </div>

      <div className="h-4 w-px bg-border/40 shrink-0" />

      {/* Active chips + add filter */}
      <div className="flex items-center gap-1.5 flex-wrap flex-1 min-w-0">
        {/* VIP chip */}
        {hasVip && (
          <Badge
            variant="outline"
            className="text-[11px] h-7 pl-2 pr-1 rounded-full font-medium bg-amber-50 border-amber-200/60 text-amber-700 gap-1 shrink-0 transition-all"
          >
            <Crown className="h-3 w-3" />
            VIP Only
            <button
              onClick={onToggleVip}
              className="ml-0.5 h-4 w-4 rounded-full inline-flex items-center justify-center hover:bg-amber-100 transition-colors"
            >
              <X className="h-3 w-3" />
            </button>
          </Badge>
        )}

        {/* Filter chips */}
        {activeChips.map((chip) => (
          <Badge
            key={`${chip.key}-${chip.value}`}
            variant="outline"
            className="text-[11px] h-7 pl-2.5 pr-1 rounded-full font-medium bg-card border-foreground/10 text-foreground/80 gap-1 shrink-0 transition-all"
          >
            {chip.label}
            <button
              onClick={() => onToggle(chip.key, chip.value)}
              className="ml-0.5 h-4 w-4 rounded-full inline-flex items-center justify-center hover:bg-accent transition-colors"
            >
              <X className="h-3 w-3" />
            </button>
          </Badge>
        ))}

        {/* Add filter popover */}
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className={cn(
                "h-7 text-[11px] rounded-full gap-1 px-2.5 text-muted-foreground hover:text-foreground transition-all",
                !hasAny && "border border-dashed border-border/50"
              )}
            >
              <SlidersHorizontal className="h-3 w-3" />
              {hasAny ? "Filter" : "Add filter"}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-60 p-2 rounded-xl shadow-lg" align="start">
            <div className="flex flex-col gap-0.5 max-h-[420px] overflow-y-auto scrollbar-autohide">
              {/* VIP toggle */}
              <div>
                <div className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-wider px-2 pt-1 pb-1.5">
                  Customer
                </div>
                <button
                  onClick={onToggleVip}
                  className={cn(
                    "w-full flex items-center gap-2 text-xs px-2 py-1.5 rounded-lg transition-all",
                    filters.vip === true
                      ? "bg-amber-50 text-amber-700 font-medium"
                      : "hover:bg-accent text-foreground"
                  )}
                >
                  <Crown className="h-3 w-3" />
                  VIP Customers
                  {filters.vip === true && (
                    <span className="ml-auto text-[10px] text-amber-500 font-medium">active</span>
                  )}
                </button>
              </div>

              {/* Category sections */}
              {filterSections.map((section) => {
                const selected = filters[section.key] as string[]
                return (
                  <div key={section.key}>
                    <div className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-wider px-2 pt-2.5 pb-1.5">
                      {section.label}
                    </div>
                    <div className="flex flex-wrap gap-1 px-1">
                      {section.options.map((opt) => {
                        const isActive = selected.includes(opt.value)
                        return (
                          <button
                            key={opt.value}
                            onClick={() => onToggle(section.key, opt.value)}
                            className={cn(
                              "inline-flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded-full border transition-all duration-150",
                              isActive
                                ? "bg-foreground text-background border-foreground font-medium scale-[1.02]"
                                : "bg-card border-border/60 text-foreground/80 hover:border-foreground/20 hover:bg-accent/30"
                            )}
                          >
                            {opt.dot && (
                              <span
                                className={cn(
                                  "h-1.5 w-1.5 rounded-full shrink-0",
                                  isActive ? "bg-background/70" : opt.dot
                                )}
                              />
                            )}
                            {opt.label}
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )
              })}
            </div>
          </PopoverContent>
        </Popover>

        {/* Clear all */}
        {hasAny && (
          <button
            onClick={onClearAll}
            className="text-[11px] text-muted-foreground/70 hover:text-foreground transition-colors ml-1 shrink-0"
          >
            Clear all
          </button>
        )}
      </div>
    </div>
  )
}
