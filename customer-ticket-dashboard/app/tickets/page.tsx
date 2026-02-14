"use client"

import { Suspense, useMemo, useState, useCallback, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { useTickets } from "@/hooks/use-tickets"
import { TicketTable } from "@/components/ticket-table"
import { FilterBar } from "@/components/filter-bar"
import { defaultFilters, filterTickets, type TicketFilters, type FilterKey } from "@/lib/filters"
import { TicketsListSkeleton } from "@/components/skeletons"

/** Read initial filters from URL search params */
function filtersFromParams(params: URLSearchParams): TicketFilters {
  const f = { ...defaultFilters }

  const topic = params.get("topic")
  if (topic) f.topic = [topic]

  const sentiment = params.get("sentiment")
  if (sentiment) f.sentiment = sentiment.split(",") as TicketFilters["sentiment"]

  const emotion = params.get("emotion")
  if (emotion) f.emotional_tone = emotion.split(",") as TicketFilters["emotional_tone"]

  const status = params.get("status")
  if (status) f.status = status.split(",") as TicketFilters["status"]

  const priority = params.get("priority")
  if (priority) f.priority = priority.split(",")

  const vip = params.get("vip")
  if (vip === "true") f.vip = true

  const search = params.get("q")
  if (search) f.search = search

  return f
}

export default function TicketsPage() {
  return (
    <Suspense fallback={<TicketsListSkeleton />}>
      <TicketsPageContent />
    </Suspense>
  )
}

function TicketsPageContent() {
  const { tickets, loading, error, refetch } = useTickets()
  const searchParams = useSearchParams()
  const [filters, setFilters] = useState<TicketFilters>(() => filtersFromParams(searchParams))
  const [initialized, setInitialized] = useState(false)

  // Re-sync if URL changes (e.g., navigating from dashboard links)
  useEffect(() => {
    if (!initialized) {
      setInitialized(true)
      return
    }
    setFilters(filtersFromParams(searchParams))
  }, [searchParams]) // eslint-disable-line react-hooks/exhaustive-deps

  const onToggle = useCallback((key: FilterKey, value: string) => {
    setFilters((prev) => {
      const arr = prev[key] as string[]
      return {
        ...prev,
        [key]: arr.includes(value) ? arr.filter((v) => v !== value) : [...arr, value],
      }
    })
  }, [])

  const onToggleVip = useCallback(() => {
    setFilters((prev) => ({ ...prev, vip: prev.vip === true ? null : true }))
  }, [])

  const onSearch = useCallback((value: string) => {
    setFilters((prev) => ({ ...prev, search: value }))
  }, [])

  const onClearAll = useCallback(() => setFilters(defaultFilters), [])

  const filteredTickets = useMemo(() => filterTickets(tickets, filters), [tickets, filters])

  if (loading) return <TicketsListSkeleton />

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">All Tickets</h1>
        <p className="text-sm text-muted-foreground mt-1">
          {filteredTickets.length === tickets.length ? (
            <><span className="tabular-nums font-medium text-foreground">{tickets.length}</span> tickets</>
          ) : (
            <>
              <span className="tabular-nums font-medium text-foreground">{filteredTickets.length}</span>
              <span className="text-muted-foreground/40 mx-1">/</span>
              <span className="tabular-nums">{tickets.length}</span> tickets
            </>
          )}
        </p>
      </div>

      {/* Error banner */}
      {error && (
        <div className="rounded-xl bg-amber-50 border border-amber-200/60 px-4 py-3 flex items-center justify-between">
          <p className="text-xs text-amber-800">
            Unable to reach the API — showing cached data.
          </p>
          <button
            onClick={refetch}
            className="text-xs font-medium text-amber-700 hover:text-amber-900 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Floating card */}
      <div className="rounded-2xl bg-card border border-border/50 shadow-sm overflow-hidden">
        <FilterBar
          filters={filters}
          onToggle={onToggle}
          onToggleVip={onToggleVip}
          onSearch={onSearch}
          onClearAll={onClearAll}
        />
        <div className="max-h-[calc(100vh-16rem)] overflow-auto scrollbar-autohide">
          <TicketTable tickets={filteredTickets} />
        </div>
      </div>
    </div>
  )
}
