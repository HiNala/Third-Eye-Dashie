import type { TicketSentiment, EmotionalTone, TicketStatus } from "./types"

export function getStatusColor(status: TicketStatus) {
  const map: Record<TicketStatus, string> = {
    open: "bg-amber-50 text-amber-700 border-amber-200/80",
    in_progress: "bg-sky-50 text-sky-700 border-sky-200/80",
    closed: "bg-secondary text-muted-foreground border-border",
  }
  return map[status]
}

export function getPriorityDot(priority: string) {
  const map: Record<string, string> = { urgent: "bg-red-500", high: "bg-orange-500", normal: "bg-amber-400", low: "bg-border" }
  return map[priority] ?? "bg-border"
}

export function getSentimentStyle(sentiment: TicketSentiment | null) {
  if (!sentiment) return "bg-secondary text-muted-foreground border-border"
  const map: Record<TicketSentiment, string> = {
    positive: "bg-emerald-50 text-emerald-600 border-emerald-200/60",
    negative: "bg-rose-50 text-rose-600 border-rose-200/60",
    neutral: "bg-secondary text-muted-foreground border-border",
  }
  return map[sentiment]
}

export function getEmotionalToneStyle(tone: EmotionalTone | null) {
  if (!tone) return "bg-secondary text-muted-foreground border-border"
  const map: Record<EmotionalTone, string> = {
    angry: "bg-rose-50 text-rose-700 border-rose-200/60",
    frustrated: "bg-orange-50 text-orange-600 border-orange-200/60",
    delighted: "bg-emerald-50 text-emerald-600 border-emerald-200/60",
    happy: "bg-amber-50 text-amber-600 border-amber-200/60",
    neutral: "bg-secondary text-muted-foreground border-border",
  }
  return map[tone]
}

export function getTopicStyle(topic: string) {
  const map: Record<string, string> = {
    product: "bg-slate-100 text-slate-600 border-slate-200/60",
    shipping: "bg-sky-50 text-sky-600 border-sky-200/60",
    billing: "bg-violet-50 text-violet-600 border-violet-200/60",
    returns: "bg-teal-50 text-teal-600 border-teal-200/60",
    "feature-request": "bg-indigo-50 text-indigo-600 border-indigo-200/60",
    warranty: "bg-amber-50 text-amber-600 border-amber-200/60",
    accessories: "bg-stone-100 text-stone-600 border-stone-200/60",
    company: "bg-slate-100 text-slate-600 border-slate-200/60",
  }
  return map[topic] ?? "bg-secondary text-muted-foreground border-border"
}

export function formatTimeAgo(dateString: string) {
  const now = new Date()
  const date = new Date(dateString)
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${diffDays}d ago`
}

export function formatTime(dateString: string) {
  return new Date(dateString).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })
}

export function formatDateGroup(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - date.getTime()) / 86400000)
  if (diffDays === 0) return "Today"
  if (diffDays === 1) return "Yesterday"
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
}

export const sentimentLabels: Record<TicketSentiment, string> = { positive: "Positive", negative: "Negative", neutral: "Neutral" }
export const emotionalToneLabels: Record<EmotionalTone, string> = { angry: "Angry", frustrated: "Frustrated", delighted: "Delighted", happy: "Happy", neutral: "Neutral" }
export const statusLabels: Record<TicketStatus, string> = { open: "Open", in_progress: "In Progress", closed: "Closed" }
