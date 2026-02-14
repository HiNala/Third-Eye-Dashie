"use client"

import { useState, useEffect, useCallback } from "react"
import type { Ticket } from "@/lib/types"
import { mockTickets } from "@/lib/mock-data"
import * as api from "@/lib/api-client"

const USE_MOCK = !process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_USE_MOCK === "true"

export function useTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      if (USE_MOCK) {
        await new Promise((r) => setTimeout(r, 200))
        setTickets([...mockTickets])
      } else {
        const res = await api.fetchTickets()
        setTickets(res.tickets ?? [])
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)))
      setTickets([...mockTickets])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { refetch() }, [refetch])
  return { tickets, loading, error, refetch, setTickets }
}

export function useTicket(id: string | null) {
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [loading, setLoading] = useState(!!id)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    if (!id) { setTicket(null); setLoading(false); return }
    setLoading(true)
    setError(null)
    if (USE_MOCK) {
      setTimeout(() => { setTicket(mockTickets.find((t) => t.id === id) ?? null); setLoading(false) }, 100)
    } else {
      api.fetchTicket(id).then(setTicket).catch((e) => { setError(e instanceof Error ? e : new Error(String(e))); setTicket(mockTickets.find((t) => t.id === id) ?? null) }).finally(() => setLoading(false))
    }
  }, [id])
  return { ticket, setTicket, loading, error }
}

