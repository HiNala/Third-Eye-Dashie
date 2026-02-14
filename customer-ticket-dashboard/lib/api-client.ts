import type { Ticket, TicketsResponse, IngestRequest, IngestResponse } from "./types"
import { normalizeTicket } from "./types"

const API_BASE =
  typeof window !== "undefined"
    ? (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1")
    : "http://localhost:8000/api/v1"

async function fetcher<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  })
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`)
  }
  return res.json() as Promise<T>
}

export async function fetchTickets(): Promise<TicketsResponse> {
  const raw = await fetcher<{ tickets: Record<string, unknown>[]; count: number }>("/tickets")
  return {
    tickets: (raw.tickets ?? []).map(normalizeTicket),
    count: raw.count,
  }
}

export async function fetchTicket(id: string): Promise<Ticket> {
  const raw = await fetcher<Record<string, unknown>>(`/tickets/${id}`)
  return normalizeTicket(raw)
}

export async function updateTags(id: string, tags: Array<{ category: string; value: string }>): Promise<Ticket> {
  const raw = await fetcher<Record<string, unknown>>(`/tickets/${id}/tags`, { method: "POST", body: JSON.stringify({ tags }) })
  return normalizeTicket(raw)
}

export async function updateStatus(id: string, status: string): Promise<Ticket> {
  const raw = await fetcher<Record<string, unknown>>(`/tickets/${id}/status`, { method: "POST", body: JSON.stringify({ status }) })
  return normalizeTicket(raw)
}

export async function updateAnalysis(id: string, updates: { sentiment?: string; emotional_tone?: string }): Promise<Ticket> {
  const raw = await fetcher<Record<string, unknown>>(`/tickets/${id}/analysis`, { method: "POST", body: JSON.stringify(updates) })
  return normalizeTicket(raw)
}

export async function ingestTickets(payload: IngestRequest): Promise<IngestResponse> {
  return fetcher<IngestResponse>("/ingest", { method: "POST", body: JSON.stringify(payload) })
}
