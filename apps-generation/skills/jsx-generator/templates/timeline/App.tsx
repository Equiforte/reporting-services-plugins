import { useEffect, useState } from "react"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Badge } from "@/components/ui/badge"

interface TimelineEvent {
  date: string
  iso_date: string
  title: string
  description: string
  status: "completed" | "in-progress" | "upcoming" | "blocked"
  tags?: string[]
  details?: Record<string, string>
}

interface TimelineData {
  meta: { title: string; generated_at: string; confidential: boolean; firm?: string; sources?: string[] }
  timeline: {
    title: string
    events: TimelineEvent[]
  }
}

const statusColors: Record<string, string> = {
  completed: "var(--brand-positive, #1A7A3A)",
  "in-progress": "var(--brand-accent, #2E75B6)",
  upcoming: "#9CA3AF",
  blocked: "var(--brand-negative, #C4261D)",
}

const statusLabels: Record<string, string> = {
  completed: "Completed",
  "in-progress": "In Progress",
  upcoming: "Upcoming",
  blocked: "Blocked",
}

export default function App() {
  const [data, setData] = useState<TimelineData | null>(null)
  const [openEvents, setOpenEvents] = useState<Set<number>>(new Set())

  useEffect(() => {
    fetch("./data.json")
      .then((r) => r.json())
      .then(setData)
      .catch(console.error)
  }, [])

  if (!data) return <div className="p-8 text-center">Loading...</div>

  const toggleEvent = (idx: number) => {
    setOpenEvents((prev) => {
      const next = new Set(prev)
      if (next.has(idx)) next.delete(idx)
      else next.add(idx)
      return next
    })
  }

  const events = [...data.timeline.events].sort(
    (a, b) => new Date(a.iso_date).getTime() - new Date(b.iso_date).getTime()
  )

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="border-b px-6 py-4 flex items-center justify-between" style={{ backgroundColor: "var(--brand-primary)", color: "white" }}>
        <div className="flex items-center gap-3">
          <img src="./logo.png" alt="Logo" className="h-8" onError={(e) => (e.currentTarget.style.display = "none")} />
          <h1 className="text-xl font-bold">{data.meta.title}</h1>
        </div>
        <span className="text-sm opacity-80">{new Date(data.meta.generated_at).toLocaleDateString()}</span>
      </header>

      <main className="flex-1 p-6">
        <h2 className="text-2xl font-bold mb-8" style={{ color: "var(--brand-heading)" }}>{data.timeline.title}</h2>

        <div className="max-w-2xl mx-auto space-y-0">
          {events.map((event, i) => (
            <div key={i} className="flex gap-4">
              {/* Timeline connector */}
              <div className="flex flex-col items-center">
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0 mt-1.5"
                  style={{ backgroundColor: statusColors[event.status] }}
                />
                {i < events.length - 1 && (
                  <div className="w-px flex-1 min-h-[2rem]" style={{ backgroundColor: "var(--brand-border, #D1D5DB)" }} />
                )}
              </div>

              {/* Event content */}
              <div className="pb-6 flex-1">
                <Collapsible open={openEvents.has(i)} onOpenChange={() => toggleEvent(i)}>
                  <CollapsibleTrigger className="w-full text-left cursor-pointer hover:opacity-80 transition-opacity">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="font-semibold" style={{ color: "var(--brand-heading)" }}>{event.title}</span>
                      <Badge
                        variant="outline"
                        className="text-xs"
                        style={{ borderColor: statusColors[event.status], color: statusColors[event.status] }}
                      >
                        {statusLabels[event.status]}
                      </Badge>
                    </div>
                    <div className="text-xs text-muted-foreground">{event.date}</div>
                  </CollapsibleTrigger>

                  <CollapsibleContent className="mt-2">
                    <p className="text-sm text-muted-foreground mb-2">{event.description}</p>

                    {event.tags && event.tags.length > 0 && (
                      <div className="flex gap-1 mb-2">
                        {event.tags.map((tag, j) => (
                          <Badge key={j} variant="secondary" className="text-xs">{tag}</Badge>
                        ))}
                      </div>
                    )}

                    {event.details && Object.keys(event.details).length > 0 && (
                      <div className="bg-muted/50 rounded p-3 text-sm space-y-1">
                        {Object.entries(event.details).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-muted-foreground">{key}</span>
                            <span className="font-medium">{value}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </CollapsibleContent>
                </Collapsible>
              </div>
            </div>
          ))}
        </div>

        {/* Sources */}
        {data.meta.sources && data.meta.sources.length > 0 && (
          <div className="mt-8 text-xs text-muted-foreground italic max-w-2xl mx-auto">
            Sources: {data.meta.sources.join(", ")}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t px-6 py-3 text-xs text-muted-foreground flex justify-between">
        <span>{data.meta.confidential ? "CONFIDENTIAL — For internal use only." : ""}</span>
        <span>{data.meta.firm}</span>
      </footer>
    </div>
  )
}
