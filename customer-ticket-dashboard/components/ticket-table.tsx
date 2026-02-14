"use client"

import Link from "next/link"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import type { Ticket } from "@/lib/types"
import {
  getStatusColor,
  getPriorityDot,
  getSentimentStyle,
  getEmotionalToneStyle,
  getTopicStyle,
  formatTimeAgo,
  statusLabels,
  sentimentLabels,
  emotionalToneLabels,
} from "@/lib/tag-styles"

interface TicketTableProps {
  tickets: Ticket[]
}

function getPriority(t: Ticket) {
  return (t.tags ?? []).find((tg) => tg.category === "priority")?.value ?? "normal"
}

function getTopics(t: Ticket) {
  return (t.tags ?? []).filter((tg) => tg.category === "topics").map((tg) => tg.value)
}

export function TicketTable({ tickets }: TicketTableProps) {
  if (tickets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-1">
        <p className="text-sm text-muted-foreground">No tickets match your filters</p>
        <p className="text-xs text-muted-foreground/50">Try adjusting or clearing filters</p>
      </div>
    )
  }

  return (
    <div className="min-w-[900px]">
      {/* Column header */}
      <div className="flex items-center gap-3 px-5 py-2.5 text-[10px] uppercase tracking-wider text-muted-foreground/80 font-medium border-b border-border/30 bg-secondary/20 sticky top-0 z-10 backdrop-blur-sm">
        <div className="w-10 shrink-0" />
        <div className="flex-1 min-w-0">Title</div>
        <div className="w-20 shrink-0">Sentiment</div>
        <div className="w-20 shrink-0">Emotion</div>
        <div className="w-28 shrink-0">Topics</div>
        <div className="w-[72px] shrink-0 text-center">Confidence</div>
        <div className="w-[66px] shrink-0 text-right">Status</div>
        <div className="w-10 shrink-0 text-right">Age</div>
      </div>

      {/* Rows */}
      {tickets.map((ticket, i) => (
        <Link key={ticket.id} href={`/tickets/${ticket.id}`} className="block group">
          <div
            className={cn(
              "flex items-center gap-3 px-5 py-3 transition-all duration-150 cursor-pointer",
              "hover:bg-accent/30",
              i !== tickets.length - 1 && "border-b border-border/20"
            )}
          >
            {/* Priority dot + ID */}
            <div className="w-10 shrink-0 flex items-center gap-1.5">
              <span className={cn("h-2 w-2 rounded-full shrink-0 transition-transform group-hover:scale-110", getPriorityDot(getPriority(ticket)))} />
              <span className="text-[10px] font-mono text-muted-foreground/50">{ticket.id.slice(0, 4)}</span>
            </div>

            {/* Title + customer */}
            <div className="flex-1 min-w-0 flex flex-col">
              <p className="text-[13px] font-medium text-foreground truncate group-hover:text-foreground/80 transition-colors">
                {ticket.title}
              </p>
              <p className="text-[11px] text-muted-foreground/70 truncate flex items-center gap-1">
                {ticket.is_vip && <span className="text-amber-600 font-semibold text-[10px]">VIP</span>}
                {ticket.customer_name} · {ticket.customer_email}
              </p>
            </div>

            {/* Sentiment */}
            <div className="w-20 shrink-0">
              <Badge variant="outline" className={cn("text-[10px] px-1.5 py-0 h-[18px] rounded-full font-normal", getSentimentStyle(ticket.sentiment))}>
                {ticket.sentiment ? sentimentLabels[ticket.sentiment] : "Pending"}
              </Badge>
            </div>

            {/* Emotion */}
            <div className="w-20 shrink-0">
              <Badge variant="outline" className={cn("text-[10px] px-1.5 py-0 h-[18px] rounded-full font-normal", getEmotionalToneStyle(ticket.emotional_tone))}>
                {ticket.emotional_tone ? emotionalToneLabels[ticket.emotional_tone] : "Pending"}
              </Badge>
            </div>

            {/* Topics */}
            <div className="w-28 shrink-0 flex items-center gap-1 flex-wrap">
              {getTopics(ticket).slice(0, 2).map((topic) => (
                <Badge key={topic} variant="outline" className={cn("text-[10px] px-1.5 py-0 h-[18px] rounded-full font-normal capitalize", getTopicStyle(topic))}>
                  {topic.replace(/-/g, " ")}
                </Badge>
              ))}
              {getTopics(ticket).length > 2 && <span className="text-[10px] text-muted-foreground/50">+{getTopics(ticket).length - 2}</span>}
            </div>

            {/* Confidence */}
            <div className="w-[72px] shrink-0 flex items-center justify-center gap-1.5">
              <div className="h-1 w-8 rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full rounded-full bg-primary/50 transition-all duration-300"
                  style={{ width: `${(ticket.confidence ?? 0) * 100}%` }}
                />
              </div>
              <span className="text-[10px] font-mono text-muted-foreground/60 tabular-nums">
                {((ticket.confidence ?? 0) * 100).toFixed(0)}%
              </span>
            </div>

            {/* Status */}
            <div className="w-[66px] shrink-0 flex justify-end">
              <Badge variant="outline" className={cn("text-[10px] px-1.5 py-0 h-[18px] rounded-full font-medium", getStatusColor(ticket.status))}>
                {statusLabels[ticket.status]}
              </Badge>
            </div>

            {/* Age */}
            <div className="w-10 shrink-0 text-right">
              <span className="text-[11px] text-muted-foreground/70">{formatTimeAgo(ticket.created_at)}</span>
            </div>
          </div>
        </Link>
      ))}
    </div>
  )
}
