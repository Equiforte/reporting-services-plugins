import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface ComparisonItem {
  name: string
  subtitle?: string
  highlighted?: boolean
  attributes: Record<string, { value: string; raw_value?: string | number; better?: "higher" | "lower" | null }>
}

interface ComparisonData {
  meta: { title: string; generated_at: string; confidential: boolean; firm?: string; sources?: string[] }
  comparison: {
    title: string
    items: ComparisonItem[]
    attribute_labels: Record<string, string>
  }
}

export default function App() {
  const [data, setData] = useState<ComparisonData | null>(null)

  useEffect(() => {
    fetch("./data.json")
      .then((r) => r.json())
      .then(setData)
      .catch(console.error)
  }, [])

  if (!data) return <div className="p-8 text-center">Loading...</div>

  const { comparison } = data
  const attributeKeys = Object.keys(comparison.attribute_labels)

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
        <h2 className="text-2xl font-bold mb-6" style={{ color: "var(--brand-heading)" }}>{comparison.title}</h2>

        <div className="grid gap-6" style={{ gridTemplateColumns: `repeat(${Math.min(comparison.items.length, 4)}, 1fr)` }}>
          {comparison.items.map((item, i) => (
            <Card
              key={i}
              className={item.highlighted ? "ring-2" : ""}
              style={{
                borderRadius: "var(--brand-card-radius)",
                boxShadow: "var(--brand-card-shadow)",
                ...(item.highlighted ? { borderColor: "var(--brand-primary)" } : {}),
              }}
            >
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{item.name}</CardTitle>
                  {item.highlighted && (
                    <Badge style={{ backgroundColor: "var(--brand-accent)" }}>Recommended</Badge>
                  )}
                </div>
                {item.subtitle && (
                  <CardDescription className="text-lg font-semibold" style={{ color: "var(--brand-primary)" }}>
                    {item.subtitle}
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {attributeKeys.map((key) => {
                    const attr = item.attributes[key]
                    if (!attr) return null
                    return (
                      <div key={key} className="flex justify-between py-2 border-b last:border-0">
                        <span className="text-sm text-muted-foreground">{comparison.attribute_labels[key]}</span>
                        <span className="text-sm font-medium">{attr.value}</span>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Sources */}
        {data.meta.sources && data.meta.sources.length > 0 && (
          <div className="mt-8 text-xs text-muted-foreground italic">
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
