"use client"

import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Smile, Frown, Meh, Angry, Heart, Sparkles } from "lucide-react"
import type { Ticket, Demographics, EmotionalTone, DemographicField } from "@/lib/types"
import { getSentimentStyle, getEmotionalToneStyle, getTopicStyle, sentimentLabels, emotionalToneLabels } from "@/lib/tag-styles"

const emotionIcons: Record<EmotionalTone, React.ReactNode> = {
  angry: <Angry className="h-4.5 w-4.5 text-rose-600" />,
  frustrated: <Frown className="h-4.5 w-4.5 text-orange-600" />,
  happy: <Smile className="h-4.5 w-4.5 text-amber-600" />,
  delighted: <Heart className="h-4.5 w-4.5 text-emerald-600" />,
  neutral: <Meh className="h-4.5 w-4.5 text-muted-foreground" />,
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = (value * 100).toFixed(0)
  return (
    <div className="flex items-center gap-2.5 mt-1.5">
      <div className="h-1.5 flex-1 rounded-full bg-muted overflow-hidden">
        <div
          className="h-full rounded-full bg-primary/60 transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[11px] font-mono text-muted-foreground tabular-nums">{pct}%</span>
    </div>
  )
}

function DemographicRow({ label, value, confidence }: { label: string; value: string; confidence: number }) {
  return (
    <div className={cn("flex items-center justify-between py-1", confidence < 0.5 && "opacity-50")}>
      <span className="text-xs text-muted-foreground capitalize">{label.replace(/_/g, " ")}</span>
      <span className="text-xs font-medium text-foreground">{value}</span>
    </div>
  )
}

/* ── Section wrapper ─────────────────────────────────────────── */

function Section({ label, children, last }: { label: string; children: React.ReactNode; last?: boolean }) {
  return (
    <div className={cn("px-5 py-4", !last && "border-b border-border/30")}>
      <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
        {label}
      </span>
      <div className="mt-2">{children}</div>
    </div>
  )
}

/* ── Panel ────────────────────────────────────────────────────── */

interface AiAnalysisPanelProps {
  ticket: Ticket
}

export function AiAnalysisPanel({ ticket }: AiAnalysisPanelProps) {
  const tags = ticket.tags ?? []
  const topicTags = tags.filter((t) => t.category === "topics")
  const priorityTag = tags.find((t) => t.category === "priority")
  const demographics = ticket.demographics

  return (
    <div className="rounded-2xl border border-border/50 shadow-sm bg-card overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-border/40 flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-primary" />
        <h2 className="text-sm font-semibold text-foreground">AI Analysis</h2>
      </div>

      {/* Sentiment */}
      <Section label="Sentiment">
        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className={cn("text-xs px-2.5 py-0.5 rounded-full font-medium", getSentimentStyle(ticket.sentiment))}
          >
            {ticket.sentiment ? sentimentLabels[ticket.sentiment] : "Pending"}
          </Badge>
        </div>
        <ConfidenceBar value={ticket.confidence ?? 0} />
      </Section>

      {/* Emotional Tone */}
      <Section label="Emotional Tone">
        <div className="flex items-center gap-2">
          {ticket.emotional_tone ? emotionIcons[ticket.emotional_tone] : <Meh className="h-4.5 w-4.5 text-muted-foreground" />}
          <Badge
            variant="outline"
            className={cn("text-xs px-2.5 py-0.5 rounded-full font-medium", getEmotionalToneStyle(ticket.emotional_tone))}
          >
            {ticket.emotional_tone ? emotionalToneLabels[ticket.emotional_tone] : "Pending"}
          </Badge>
        </div>
      </Section>

      {/* Tags */}
      <Section label="AI Tags">
        {topicTags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {topicTags.map((tag) => (
              <Badge
                key={tag.value}
                variant="outline"
                className={cn("text-[11px] px-2 py-0.5 rounded-full capitalize", getTopicStyle(tag.value))}
              >
                {tag.value.replace(/-/g, " ")}
              </Badge>
            ))}
          </div>
        )}
        {priorityTag && (
          <div className={cn(topicTags.length > 0 && "mt-2")}>
            <Badge variant="outline" className="text-[11px] px-2 py-0.5 rounded-full capitalize">
              {priorityTag.value}
            </Badge>
          </div>
        )}
        {tags.length === 0 && (
          <p className="text-xs text-muted-foreground italic">Processing...</p>
        )}
      </Section>

      {/* Demographics */}
      {demographics && Object.keys(demographics).length > 0 && (
        <Section label="Demographics">
          <div className="flex flex-col -my-0.5">
            {(Object.entries(demographics) as [keyof Demographics, DemographicField | null | undefined][]).map(
              ([key, field]) =>
                field && field.value ? (
                  <DemographicRow key={key} label={key} value={field.value} confidence={field.confidence} />
                ) : null
            )}
          </div>
        </Section>
      )}

      {/* Metadata */}
      <Section label="Metadata" last>
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Customer</span>
            <span className="text-xs font-medium text-foreground">{ticket.customer_name}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Email</span>
            <span className="text-xs font-medium text-foreground truncate max-w-[180px]">{ticket.customer_email}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Created</span>
            <span className="text-xs font-medium text-foreground">{new Date(ticket.created_at).toLocaleDateString()}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Updated</span>
            <span className="text-xs font-medium text-foreground">{new Date(ticket.last_updated).toLocaleDateString()}</span>
          </div>
        </div>
      </Section>
    </div>
  )
}
