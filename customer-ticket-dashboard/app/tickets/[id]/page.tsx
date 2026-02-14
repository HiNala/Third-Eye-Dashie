"use client"

import { use, useState, useCallback } from "react"
import Link from "next/link"
import {
  ArrowLeft,
  Check,
  Loader2,
  Clock,
  Mail,
  User,
  Calendar,
  Send,
  Square,
  Hash,
  Crown,
} from "lucide-react"
import { useTicket } from "@/hooks/use-tickets"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  PromptInput,
  PromptInputTextarea,
  PromptInputActions,
  PromptInputAction,
} from "@/components/ui/prompt-input"
import { AiAnalysisPanel } from "@/components/ai-analysis-panel"
import { TicketDetailSkeleton } from "@/components/skeletons"
import {
  getStatusColor,
  statusLabels,
  formatTimeAgo,
  getSentimentStyle,
  getEmotionalToneStyle,
  sentimentLabels,
  emotionalToneLabels,
} from "@/lib/tag-styles"
import { cn } from "@/lib/utils"
import * as api from "@/lib/api-client"
import type { TicketStatus } from "@/lib/types"

export default function TicketDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const resolvedParams = use(params)
  const { ticket, loading } = useTicket(resolvedParams.id)
  const [currentStatus, setCurrentStatus] = useState<TicketStatus | null>(null)
  const [statusSaving, setStatusSaving] = useState(false)
  const [statusSaved, setStatusSaved] = useState(false)
  const [statusError, setStatusError] = useState<string | null>(null)
  const [replyText, setReplyText] = useState("")
  const [replySending, setReplySending] = useState(false)
  const [replySent, setReplySent] = useState(false)

  const displayStatus = currentStatus ?? ticket?.status ?? "open"

  const handleStatusChange = useCallback(
    async (newStatus: string) => {
      if (!ticket) return
      const prev = displayStatus
      setCurrentStatus(newStatus as TicketStatus)
      setStatusSaving(true)
      setStatusError(null)
      setStatusSaved(false)
      try {
        await api.updateStatus(ticket.id, newStatus)
        setStatusSaved(true)
        setTimeout(() => setStatusSaved(false), 2000)
      } catch {
        setCurrentStatus(prev as TicketStatus)
        setStatusError("Failed to update status")
        setTimeout(() => setStatusError(null), 3000)
      } finally {
        setStatusSaving(false)
      }
    },
    [ticket, displayStatus]
  )

  const handleSendReply = useCallback(() => {
    if (!replyText.trim() || !ticket) return
    setReplySending(true)
    // Simulated send — this would hit an API endpoint in production
    setTimeout(() => {
      setReplySending(false)
      setReplySent(true)
      setReplyText("")
      setTimeout(() => setReplySent(false), 3000)
    }, 1200)
  }, [replyText, ticket])

  if (loading) return <TicketDetailSkeleton />

  if (!ticket) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <p className="text-sm text-muted-foreground">Ticket not found</p>
        <Link
          href="/tickets"
          className="text-xs text-primary hover:underline inline-flex items-center gap-1"
        >
          <ArrowLeft className="h-3 w-3" /> Back to tickets
        </Link>
      </div>
    )
  }

  const topicTags = (ticket.tags ?? []).filter((t) => t.category === "topics")
  const priorityTag = (ticket.tags ?? []).find(
    (t) => t.category === "priority"
  )

  return (
    <div className="flex flex-col gap-5">
      {/* Back link */}
      <Link
        href="/tickets"
        className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors w-fit group"
      >
        <ArrowLeft className="h-3.5 w-3.5 transition-transform group-hover:-translate-x-0.5" />{" "}
        Back to tickets
      </Link>

      {/* ── Header card ─────────────────────────────────────── */}
      <div className="rounded-2xl bg-card border border-border/50 shadow-sm overflow-hidden">
        <div className="px-6 py-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                {ticket.is_vip && (
                  <span className="inline-flex items-center gap-1 text-amber-600 font-medium text-[11px] bg-amber-50 border border-amber-200/60 px-2 py-0.5 rounded-full">
                    <Crown className="h-3 w-3" /> VIP
                  </span>
                )}
                {ticket.sentiment && (
                  <Badge
                    variant="outline"
                    className={cn(
                      "text-[11px] px-2 py-0 h-[22px] rounded-full font-medium",
                      getSentimentStyle(ticket.sentiment)
                    )}
                  >
                    {sentimentLabels[ticket.sentiment]}
                  </Badge>
                )}
                {ticket.emotional_tone &&
                  ticket.emotional_tone !== "neutral" && (
                    <Badge
                      variant="outline"
                      className={cn(
                        "text-[11px] px-2 py-0 h-[22px] rounded-full font-medium capitalize",
                        getEmotionalToneStyle(ticket.emotional_tone)
                      )}
                    >
                      {emotionalToneLabels[ticket.emotional_tone]}
                    </Badge>
                  )}
                {topicTags.map((tag) => (
                  <Badge
                    key={tag.value}
                    variant="outline"
                    className="text-[11px] px-2 py-0 h-[22px] rounded-full font-normal capitalize text-muted-foreground"
                  >
                    {tag.value.replace(/-/g, " ")}
                  </Badge>
                ))}
                {priorityTag && (
                  <Badge
                    variant="outline"
                    className="text-[11px] px-2 py-0 h-[22px] rounded-full font-normal capitalize text-muted-foreground"
                  >
                    {priorityTag.value}
                  </Badge>
                )}
              </div>
              <h1 className="text-lg font-semibold text-foreground leading-snug">
                {ticket.title}
              </h1>
            </div>
            <Badge
              variant="outline"
              className={cn(
                "text-xs px-3 py-1 rounded-full font-medium shrink-0",
                getStatusColor(displayStatus)
              )}
            >
              {statusLabels[displayStatus]}
            </Badge>
          </div>
        </div>

        {/* Inline metadata strip */}
        <div className="px-6 py-3 border-t border-border/30 bg-secondary/15 flex items-center gap-5 flex-wrap text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <User className="h-3.5 w-3.5 text-muted-foreground/50" />
            <span className="font-medium text-foreground">
              {ticket.customer_name}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <Mail className="h-3.5 w-3.5 text-muted-foreground/50" />
            <span>{ticket.customer_email}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Calendar className="h-3.5 w-3.5 text-muted-foreground/50" />
            <span>
              {new Date(ticket.created_at).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <Clock className="h-3.5 w-3.5 text-muted-foreground/50" />
            <span>{formatTimeAgo(ticket.created_at)}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Hash className="h-3.5 w-3.5 text-muted-foreground/50" />
            <span className="font-mono text-[11px]">
              {ticket.id.slice(0, 8)}
            </span>
          </div>
        </div>
      </div>

      {/* ── Main content grid ───────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-5">
        {/* Left column */}
        <div className="flex flex-col gap-5">
          {/* Customer message */}
          <div className="rounded-2xl bg-card border border-border/50 shadow-sm overflow-hidden">
            <div className="px-6 py-3 border-b border-border/30 flex items-center gap-2">
              <div className="h-6 w-6 rounded-full bg-secondary flex items-center justify-center shrink-0">
                <span className="text-[10px] font-bold text-muted-foreground">
                  {ticket.customer_name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .slice(0, 2)
                    .toUpperCase()}
                </span>
              </div>
              <span className="text-xs font-medium text-foreground">
                {ticket.customer_name}
              </span>
              <span className="text-[11px] text-muted-foreground/50 ml-auto">
                {new Date(ticket.created_at).toLocaleString("en-US", {
                  month: "short",
                  day: "numeric",
                  hour: "numeric",
                  minute: "2-digit",
                })}
              </span>
            </div>
            <div className="px-6 py-5">
              {ticket.content.split("\n").map((line, i) => (
                <p
                  key={i}
                  className={cn(
                    "text-[14px] leading-[1.8] text-foreground/85",
                    !line.trim() && "h-3"
                  )}
                >
                  {line || "\u00A0"}
                </p>
              ))}
            </div>
          </div>

          {/* Reply success feedback */}
          {replySent && (
            <div className="rounded-xl bg-emerald-50 border border-emerald-200/60 px-4 py-3 flex items-center gap-2">
              <Check className="h-3.5 w-3.5 text-emerald-600" />
              <p className="text-xs text-emerald-700 font-medium">
                Reply sent successfully
              </p>
            </div>
          )}

          {/* Reply box */}
          <div className="rounded-2xl bg-card border border-border/50 shadow-sm overflow-hidden">
            <div className="px-6 py-3 border-b border-border/30">
              <span className="text-xs font-medium text-foreground">
                Reply to {ticket.customer_name}
              </span>
            </div>
            <div className="p-4">
              <PromptInput
                value={replyText}
                onValueChange={setReplyText}
                isLoading={replySending}
                onSubmit={handleSendReply}
                className="border-border/40 bg-card shadow-none"
              >
                <PromptInputTextarea
                  placeholder={`Write a reply to ${ticket.customer_name}...`}
                  className="text-sm"
                />
                <PromptInputActions className="justify-between pt-2 px-1">
                  <div className="flex items-center gap-2">
                    {/* Status select inline */}
                    <div className="flex items-center gap-1.5">
                      <span className="text-[11px] text-muted-foreground">
                        Status:
                      </span>
                      <Select
                        value={displayStatus}
                        onValueChange={handleStatusChange}
                      >
                        <SelectTrigger className="h-7 text-[11px] w-[120px] rounded-lg bg-secondary/50 border-border/40">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="open">Open</SelectItem>
                          <SelectItem value="in_progress">
                            In Progress
                          </SelectItem>
                          <SelectItem value="closed">Closed</SelectItem>
                        </SelectContent>
                      </Select>
                      {statusSaving && (
                        <Loader2 className="h-3 w-3 text-muted-foreground animate-spin" />
                      )}
                      {statusSaved && (
                        <Check className="h-3 w-3 text-emerald-600" />
                      )}
                      {statusError && (
                        <span className="text-[10px] text-destructive">
                          {statusError}
                        </span>
                      )}
                    </div>
                  </div>
                  <PromptInputAction
                    tooltip={
                      replySending ? "Sending..." : "Send reply (Enter)"
                    }
                  >
                    <Button
                      variant="default"
                      size="icon"
                      className="h-8 w-8 rounded-full"
                      onClick={handleSendReply}
                      disabled={!replyText.trim() || replySending}
                    >
                      {replySending ? (
                        <Square className="h-4 w-4 fill-current" />
                      ) : (
                        <Send className="h-4 w-4" />
                      )}
                    </Button>
                  </PromptInputAction>
                </PromptInputActions>
              </PromptInput>
            </div>
          </div>

          {/* Confidence strip */}
          {ticket.confidence !== null && (
            <div className="rounded-2xl bg-card border border-border/50 shadow-sm px-6 py-4 flex items-center gap-4">
              <span className="text-[11px] text-muted-foreground font-medium shrink-0">
                AI Confidence
              </span>
              <div className="h-1.5 flex-1 rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full rounded-full bg-primary/50 transition-all duration-500"
                  style={{
                    width: `${(ticket.confidence ?? 0) * 100}%`,
                  }}
                />
              </div>
              <span className="text-xs font-mono font-medium text-foreground tabular-nums">
                {((ticket.confidence ?? 0) * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>

        {/* Right column — AI Analysis */}
        <AiAnalysisPanel ticket={ticket} />
      </div>
    </div>
  )
}
