import type { Ticket, TicketSentiment, EmotionalTone, TicketStatus } from "./types"

/**
 * Multi-select filter model.
 * Empty array = show all (no restriction).
 * One or more values = OR within category, AND across categories.
 * vip: null = all, true = VIP only, false = non-VIP only.
 */
export interface TicketFilters {
  search: string
  sentiment: TicketSentiment[]
  emotional_tone: EmotionalTone[]
  status: TicketStatus[]
  priority: string[]
  topic: string[]
  vip: boolean | null
}

export const defaultFilters: TicketFilters = {
  search: "",
  sentiment: [],
  emotional_tone: [],
  status: [],
  priority: [],
  topic: [],
  vip: null,
}

export type FilterKey = keyof Omit<TicketFilters, "search" | "vip">

export function filterTickets(tickets: Ticket[], filters: TicketFilters): Ticket[] {
  return tickets.filter((t) => {
    // text search
    if (filters.search) {
      const q = filters.search.toLowerCase()
      if (
        !t.title.toLowerCase().includes(q) &&
        !t.content.toLowerCase().includes(q) &&
        !t.customer_email.toLowerCase().includes(q) &&
        !t.customer_name.toLowerCase().includes(q)
      )
        return false
    }

    // sentiment (OR within)
    if (filters.sentiment.length > 0 && (!t.sentiment || !filters.sentiment.includes(t.sentiment)))
      return false

    // emotional tone (OR within)
    if (
      filters.emotional_tone.length > 0 &&
      (!t.emotional_tone || !filters.emotional_tone.includes(t.emotional_tone))
    )
      return false

    // status (OR within)
    if (filters.status.length > 0 && !filters.status.includes(t.status)) return false

    // priority (OR within)
    if (filters.priority.length > 0) {
      const tp = (t.tags ?? []).find((tg) => tg.category === "priority")?.value
      if (!tp || !filters.priority.includes(tp)) return false
    }

    // topic (OR within)
    if (filters.topic.length > 0) {
      const topics = (t.tags ?? []).filter((tg) => tg.category === "topics").map((tg) => tg.value)
      if (!topics.some((tp) => filters.topic.includes(tp))) return false
    }

    // VIP
    if (filters.vip !== null && t.is_vip !== filters.vip) return false

    return true
  })
}
