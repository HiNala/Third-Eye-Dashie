export interface TicketTag {
  category: string
  value: string
}

export interface DemographicField {
  value: string | null
  confidence: number
}

export interface Demographics {
  family_status?: DemographicField | null
  health_conditions?: DemographicField | null
  location?: DemographicField | null
  occupation?: DemographicField | null
  age_bracket?: DemographicField | null
}

export type TicketSentiment = "positive" | "negative" | "neutral"
export type EmotionalTone = "angry" | "happy" | "frustrated" | "delighted" | "neutral"
export type TicketStatus = "open" | "in_progress" | "closed"

export interface Ticket {
  id: string
  title: string
  content: string
  tags: TicketTag[] | null
  demographics: Demographics | null
  sentiment: TicketSentiment | null
  emotional_tone: EmotionalTone | null
  confidence: number | null
  customer_name: string
  customer_email: string
  is_vip: boolean
  status: TicketStatus
  created_at: string
  last_updated: string
}

/**
 * Normalize a raw ticket from the API.
 * The backend may not send `customer_name` or `is_vip`,
 * so we derive sensible defaults here.
 */
export function normalizeTicket(raw: Record<string, unknown>): Ticket {
  const email = (raw.customer_email as string) ?? ""
  return {
    ...(raw as unknown as Ticket),
    customer_name: (raw.customer_name as string) || email.split("@")[0].replace(/[._-]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
    is_vip: (raw.is_vip as boolean) ?? false,
  }
}

export interface TicketsResponse {
  tickets: Ticket[]
  count: number
}

export interface IngestRequest {
  tickets: Array<{
    title: string
    content: string
    customer_email: string
    status?: TicketStatus
  }>
}

export interface IngestResponse {
  accepted: boolean
  ticket_ids: string[]
  message: string
}

