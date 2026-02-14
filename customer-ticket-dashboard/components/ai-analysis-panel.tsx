"use client"

import { useState, useCallback } from "react"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  Smile,
  Frown,
  Meh,
  Angry,
  Heart,
  Sparkles,
  Pencil,
  Check,
  X,
  Loader2,
  Plus,
  Trash2,
} from "lucide-react"
import type {
  Ticket,
  TicketTag,
  Demographics,
  EmotionalTone,
  TicketSentiment,
  DemographicField,
} from "@/lib/types"
import {
  getSentimentStyle,
  getEmotionalToneStyle,
  getTopicStyle,
  sentimentLabels,
  emotionalToneLabels,
} from "@/lib/tag-styles"
import * as api from "@/lib/api-client"

/* ── Icons map ───────────────────────────────────────────────── */

const emotionIcons: Record<EmotionalTone, React.ReactNode> = {
  angry: <Angry className="h-4.5 w-4.5 text-rose-600" />,
  frustrated: <Frown className="h-4.5 w-4.5 text-orange-600" />,
  happy: <Smile className="h-4.5 w-4.5 text-amber-600" />,
  delighted: <Heart className="h-4.5 w-4.5 text-emerald-600" />,
  neutral: <Meh className="h-4.5 w-4.5 text-muted-foreground" />,
}

/* ── Confidence bar ──────────────────────────────────────────── */

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
      <span className="text-[11px] font-mono text-muted-foreground tabular-nums">
        {pct}%
      </span>
    </div>
  )
}

/* ── Demographic row ─────────────────────────────────────────── */

function DemographicRow({
  label,
  value,
  confidence,
}: {
  label: string
  value: string
  confidence: number
}) {
  return (
    <div
      className={cn(
        "flex items-center justify-between py-1",
        confidence < 0.5 && "opacity-50"
      )}
    >
      <span className="text-xs text-muted-foreground capitalize">
        {label.replace(/_/g, " ")}
      </span>
      <span className="text-xs font-medium text-foreground">{value}</span>
    </div>
  )
}

/* ── Section wrapper ─────────────────────────────────────────── */

function Section({
  label,
  children,
  last,
  onEdit,
  editing,
}: {
  label: string
  children: React.ReactNode
  last?: boolean
  onEdit?: () => void
  editing?: boolean
}) {
  return (
    <div className={cn("px-5 py-4", !last && "border-b border-border/30")}>
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
          {label}
        </span>
        {onEdit && !editing && (
          <button
            onClick={onEdit}
            className="text-muted-foreground/40 hover:text-primary transition-colors p-0.5 rounded"
            title={`Edit ${label}`}
          >
            <Pencil className="h-3 w-3" />
          </button>
        )}
      </div>
      <div className="mt-2">{children}</div>
    </div>
  )
}

/* ── Save feedback ───────────────────────────────────────────── */

function SaveFeedback({
  saving,
  saved,
  error,
}: {
  saving: boolean
  saved: boolean
  error: string | null
}) {
  if (!saving && !saved && !error) return null
  return (
    <div className="flex items-center gap-1 mt-1.5">
      {saving && (
        <span className="flex items-center gap-1 text-[10px] text-muted-foreground">
          <Loader2 className="h-2.5 w-2.5 animate-spin" /> Saving...
        </span>
      )}
      {saved && (
        <span className="flex items-center gap-1 text-[10px] text-emerald-600">
          <Check className="h-2.5 w-2.5" /> Saved
        </span>
      )}
      {error && (
        <span className="text-[10px] text-destructive">{error}</span>
      )}
    </div>
  )
}

/* ── Panel ────────────────────────────────────────────────────── */

interface AiAnalysisPanelProps {
  ticket: Ticket
  onTicketUpdate?: (updated: Ticket) => void
}

export function AiAnalysisPanel({ ticket, onTicketUpdate }: AiAnalysisPanelProps) {
  const tags = ticket.tags ?? []
  const topicTags = tags.filter((t) => t.category === "topics")
  const priorityTag = tags.find((t) => t.category === "priority")
  const demographics = ticket.demographics

  /* ── Sentiment editing state ─── */
  const [editSentiment, setEditSentiment] = useState(false)
  const [sentimentSaving, setSentimentSaving] = useState(false)
  const [sentimentSaved, setSentimentSaved] = useState(false)
  const [sentimentError, setSentimentError] = useState<string | null>(null)

  /* ── Emotional tone editing state ─── */
  const [editTone, setEditTone] = useState(false)
  const [toneSaving, setToneSaving] = useState(false)
  const [toneSaved, setToneSaved] = useState(false)
  const [toneError, setToneError] = useState<string | null>(null)

  /* ── Tags editing state ─── */
  const [editTags, setEditTags] = useState(false)
  const [localTags, setLocalTags] = useState<TicketTag[]>(tags)
  const [newTagCategory, setNewTagCategory] = useState("topics")
  const [newTagValue, setNewTagValue] = useState("")
  const [tagsSaving, setTagsSaving] = useState(false)
  const [tagsSaved, setTagsSaved] = useState(false)
  const [tagsError, setTagsError] = useState<string | null>(null)

  /* ── Handlers ─── */

  const handleSentimentChange = useCallback(
    async (newSentiment: string) => {
      setSentimentSaving(true)
      setSentimentError(null)
      setSentimentSaved(false)
      try {
        const updated = await api.updateAnalysis(ticket.id, {
          sentiment: newSentiment,
        })
        onTicketUpdate?.(updated)
        setSentimentSaved(true)
        setEditSentiment(false)
        setTimeout(() => setSentimentSaved(false), 2000)
      } catch {
        setSentimentError("Failed to update")
        setTimeout(() => setSentimentError(null), 3000)
      } finally {
        setSentimentSaving(false)
      }
    },
    [ticket.id, onTicketUpdate]
  )

  const handleToneChange = useCallback(
    async (newTone: string) => {
      setToneSaving(true)
      setToneError(null)
      setToneSaved(false)
      try {
        const updated = await api.updateAnalysis(ticket.id, {
          emotional_tone: newTone,
        })
        onTicketUpdate?.(updated)
        setToneSaved(true)
        setEditTone(false)
        setTimeout(() => setToneSaved(false), 2000)
      } catch {
        setToneError("Failed to update")
        setTimeout(() => setToneError(null), 3000)
      } finally {
        setToneSaving(false)
      }
    },
    [ticket.id, onTicketUpdate]
  )

  const handlePriorityChange = useCallback(
    async (newPriority: string) => {
      setTagsSaving(true)
      setTagsError(null)
      setTagsSaved(false)
      try {
        const otherTags = (ticket.tags ?? []).filter(
          (t) => t.category !== "priority"
        )
        const newTags = [...otherTags, { category: "priority", value: newPriority }]
        const updated = await api.updateTags(ticket.id, newTags)
        onTicketUpdate?.(updated)
        setLocalTags(updated.tags ?? [])
        setTagsSaved(true)
        setTimeout(() => setTagsSaved(false), 2000)
      } catch {
        setTagsError("Failed to update priority")
        setTimeout(() => setTagsError(null), 3000)
      } finally {
        setTagsSaving(false)
      }
    },
    [ticket.id, ticket.tags, onTicketUpdate]
  )

  const handleRemoveTag = useCallback(
    (tagToRemove: TicketTag) => {
      setLocalTags((prev) =>
        prev.filter(
          (t) =>
            !(t.category === tagToRemove.category && t.value === tagToRemove.value)
        )
      )
    },
    []
  )

  const handleAddTag = useCallback(() => {
    if (!newTagValue.trim()) return
    setLocalTags((prev) => [
      ...prev,
      {
        category: newTagCategory,
        value: newTagValue.trim().toLowerCase().replace(/\s+/g, "-"),
      },
    ])
    setNewTagValue("")
  }, [newTagCategory, newTagValue])

  const handleSaveTags = useCallback(async () => {
    setTagsSaving(true)
    setTagsError(null)
    setTagsSaved(false)
    try {
      const updated = await api.updateTags(ticket.id, localTags)
      onTicketUpdate?.(updated)
      setLocalTags(updated.tags ?? [])
      setTagsSaved(true)
      setEditTags(false)
      setTimeout(() => setTagsSaved(false), 2000)
    } catch {
      setTagsError("Failed to update tags")
      setTimeout(() => setTagsError(null), 3000)
    } finally {
      setTagsSaving(false)
    }
  }, [ticket.id, localTags, onTicketUpdate])

  const handleCancelTags = useCallback(() => {
    setLocalTags(ticket.tags ?? [])
    setEditTags(false)
    setTagsError(null)
  }, [ticket.tags])

  return (
    <div className="rounded-2xl border border-border/50 shadow-sm bg-card overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-border/40 flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-primary" />
        <h2 className="text-sm font-semibold text-foreground">AI Analysis</h2>
      </div>

      {/* ── Sentiment ─────────────────────────────────────────── */}
      <Section
        label="Sentiment"
        onEdit={() => setEditSentiment(true)}
        editing={editSentiment}
      >
        {editSentiment ? (
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center gap-2">
              <Select
                value={ticket.sentiment ?? ""}
                onValueChange={handleSentimentChange}
                disabled={sentimentSaving}
              >
                <SelectTrigger className="h-8 text-xs w-full rounded-lg bg-secondary/50 border-border/40">
                  <SelectValue placeholder="Select sentiment" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="positive">Positive</SelectItem>
                  <SelectItem value="negative">Negative</SelectItem>
                  <SelectItem value="neutral">Neutral</SelectItem>
                </SelectContent>
              </Select>
              <button
                onClick={() => setEditSentiment(false)}
                className="text-muted-foreground hover:text-foreground transition-colors p-1"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
            <SaveFeedback
              saving={sentimentSaving}
              saved={sentimentSaved}
              error={sentimentError}
            />
          </div>
        ) : (
          <>
            <div className="flex items-center gap-2">
              <Badge
                variant="outline"
                className={cn(
                  "text-xs px-2.5 py-0.5 rounded-full font-medium",
                  getSentimentStyle(ticket.sentiment)
                )}
              >
                {ticket.sentiment
                  ? sentimentLabels[ticket.sentiment]
                  : "Pending"}
              </Badge>
            </div>
            <ConfidenceBar value={ticket.confidence ?? 0} />
            <SaveFeedback
              saving={sentimentSaving}
              saved={sentimentSaved}
              error={sentimentError}
            />
          </>
        )}
      </Section>

      {/* ── Emotional Tone ────────────────────────────────────── */}
      <Section
        label="Emotional Tone"
        onEdit={() => setEditTone(true)}
        editing={editTone}
      >
        {editTone ? (
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center gap-2">
              <Select
                value={ticket.emotional_tone ?? ""}
                onValueChange={handleToneChange}
                disabled={toneSaving}
              >
                <SelectTrigger className="h-8 text-xs w-full rounded-lg bg-secondary/50 border-border/40">
                  <SelectValue placeholder="Select tone" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="angry">Angry</SelectItem>
                  <SelectItem value="frustrated">Frustrated</SelectItem>
                  <SelectItem value="happy">Happy</SelectItem>
                  <SelectItem value="delighted">Delighted</SelectItem>
                  <SelectItem value="neutral">Neutral</SelectItem>
                </SelectContent>
              </Select>
              <button
                onClick={() => setEditTone(false)}
                className="text-muted-foreground hover:text-foreground transition-colors p-1"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
            <SaveFeedback
              saving={toneSaving}
              saved={toneSaved}
              error={toneError}
            />
          </div>
        ) : (
          <>
            <div className="flex items-center gap-2">
              {ticket.emotional_tone ? (
                emotionIcons[ticket.emotional_tone]
              ) : (
                <Meh className="h-4.5 w-4.5 text-muted-foreground" />
              )}
              <Badge
                variant="outline"
                className={cn(
                  "text-xs px-2.5 py-0.5 rounded-full font-medium",
                  getEmotionalToneStyle(ticket.emotional_tone)
                )}
              >
                {ticket.emotional_tone
                  ? emotionalToneLabels[ticket.emotional_tone]
                  : "Pending"}
              </Badge>
            </div>
            <SaveFeedback
              saving={toneSaving}
              saved={toneSaved}
              error={toneError}
            />
          </>
        )}
      </Section>

      {/* ── Tags ──────────────────────────────────────────────── */}
      <Section
        label="Tags & Priority"
        onEdit={() => {
          setLocalTags(ticket.tags ?? [])
          setEditTags(true)
        }}
        editing={editTags}
      >
        {editTags ? (
          <div className="flex flex-col gap-3">
            {/* Priority inline */}
            <div className="flex items-center gap-2">
              <span className="text-[11px] text-muted-foreground shrink-0">
                Priority:
              </span>
              <Select
                value={
                  localTags.find((t) => t.category === "priority")?.value ?? ""
                }
                onValueChange={(val) => {
                  setLocalTags((prev) => {
                    const without = prev.filter(
                      (t) => t.category !== "priority"
                    )
                    return [...without, { category: "priority", value: val }]
                  })
                }}
              >
                <SelectTrigger className="h-7 text-[11px] w-[110px] rounded-lg bg-secondary/50 border-border/40">
                  <SelectValue placeholder="Priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="urgent">Urgent</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="normal">Normal</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Existing tags */}
            <div className="flex flex-wrap gap-1.5">
              {localTags
                .filter((t) => t.category !== "priority")
                .map((tag, i) => (
                  <Badge
                    key={`${tag.category}-${tag.value}-${i}`}
                    variant="outline"
                    className={cn(
                      "text-[11px] px-2 py-0.5 rounded-full capitalize flex items-center gap-1 pr-1",
                      getTopicStyle(tag.value)
                    )}
                  >
                    {tag.value.replace(/-/g, " ")}
                    <button
                      onClick={() => handleRemoveTag(tag)}
                      className="hover:text-destructive transition-colors ml-0.5"
                    >
                      <X className="h-2.5 w-2.5" />
                    </button>
                  </Badge>
                ))}
            </div>

            {/* Add new tag */}
            <div className="flex items-center gap-1.5">
              <Select
                value={newTagCategory}
                onValueChange={setNewTagCategory}
              >
                <SelectTrigger className="h-7 text-[11px] w-[90px] rounded-lg bg-secondary/50 border-border/40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="topics">Topic</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
              <Input
                value={newTagValue}
                onChange={(e) => setNewTagValue(e.target.value)}
                placeholder="Tag value..."
                className="h-7 text-[11px] flex-1 rounded-lg bg-secondary/50 border-border/40"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault()
                    handleAddTag()
                  }
                }}
              />
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 shrink-0"
                onClick={handleAddTag}
                disabled={!newTagValue.trim()}
              >
                <Plus className="h-3 w-3" />
              </Button>
            </div>

            {/* Save / Cancel */}
            <div className="flex items-center gap-2 pt-1">
              <Button
                size="sm"
                className="h-7 text-[11px] px-3 rounded-lg"
                onClick={handleSaveTags}
                disabled={tagsSaving}
              >
                {tagsSaving ? (
                  <Loader2 className="h-3 w-3 animate-spin mr-1" />
                ) : (
                  <Check className="h-3 w-3 mr-1" />
                )}
                Save Tags
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 text-[11px] px-3 rounded-lg"
                onClick={handleCancelTags}
              >
                Cancel
              </Button>
            </div>

            <SaveFeedback
              saving={tagsSaving}
              saved={tagsSaved}
              error={tagsError}
            />
          </div>
        ) : (
          <>
            {/* Priority display */}
            {priorityTag && (
              <div className="flex items-center gap-2 mb-2">
                <span className="text-[11px] text-muted-foreground">
                  Priority:
                </span>
                <Select
                  value={priorityTag.value}
                  onValueChange={handlePriorityChange}
                  disabled={tagsSaving}
                >
                  <SelectTrigger className="h-6 text-[11px] w-[100px] rounded-lg bg-secondary/30 border-border/30">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="urgent">Urgent</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="normal">Normal</SelectItem>
                    <SelectItem value="low">Low</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}

            {/* Topic tags display */}
            {topicTags.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {topicTags.map((tag) => (
                  <Badge
                    key={tag.value}
                    variant="outline"
                    className={cn(
                      "text-[11px] px-2 py-0.5 rounded-full capitalize",
                      getTopicStyle(tag.value)
                    )}
                  >
                    {tag.value.replace(/-/g, " ")}
                  </Badge>
                ))}
              </div>
            )}

            {tags.length === 0 && (
              <p className="text-xs text-muted-foreground italic">
                No tags yet
              </p>
            )}

            <SaveFeedback
              saving={tagsSaving}
              saved={tagsSaved}
              error={tagsError}
            />
          </>
        )}
      </Section>

      {/* ── Demographics ─────────────────────────────────────── */}
      {demographics && Object.keys(demographics).length > 0 && (
        <Section label="Demographics">
          <div className="flex flex-col -my-0.5">
            {(
              Object.entries(demographics) as [
                keyof Demographics,
                DemographicField | null | undefined,
              ][]
            ).map(([key, field]) =>
              field && field.value ? (
                <DemographicRow
                  key={key}
                  label={key}
                  value={field.value}
                  confidence={field.confidence}
                />
              ) : null
            )}
          </div>
        </Section>
      )}

      {/* ── Metadata ─────────────────────────────────────────── */}
      <Section label="Metadata" last>
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Customer</span>
            <span className="text-xs font-medium text-foreground">
              {ticket.customer_name}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Email</span>
            <span className="text-xs font-medium text-foreground truncate max-w-[180px]">
              {ticket.customer_email}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Created</span>
            <span className="text-xs font-medium text-foreground">
              {new Date(ticket.created_at).toLocaleDateString()}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Updated</span>
            <span className="text-xs font-medium text-foreground">
              {new Date(ticket.last_updated).toLocaleDateString()}
            </span>
          </div>
        </div>
      </Section>
    </div>
  )
}
