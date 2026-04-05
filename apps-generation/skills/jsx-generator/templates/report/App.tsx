import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import {
  Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent,
  SidebarGroupLabel, SidebarMenu, SidebarMenuItem, SidebarMenuButton,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from "@/components/ui/chart"
import { Bar, BarChart, Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts"
import type { ChartConfig } from "@/components/ui/chart"

// ── Types ──────────────────────────────────────────────────

interface Figure {
  type: "table" | "chart" | "kpi-row"
  data: {
    type?: "area" | "bar" | "line" | "pie"
    title?: string
    labels?: string[]
    datasets?: { name: string; values: number[] }[]
    columns?: { key: string; label: string; align?: string }[]
    rows?: Record<string, string | number>[]
  }
}

interface Section {
  id: string
  heading: string
  level: number
  content: string
  figures?: Figure[]
}

interface ReportData {
  meta: { title: string; generated_at: string; confidential: boolean; firm?: string; sources?: string[] }
  sections: Section[]
}

// ── Helpers ────────────────────────────────────────────────

const CHART_COLORS = [
  "var(--brand-primary)",
  "var(--brand-accent)",
  "var(--brand-positive)",
  "var(--brand-warning)",
  "var(--brand-negative)",
]

function buildChartConfig(datasets: { name: string }[]): ChartConfig {
  const config: ChartConfig = {}
  datasets.forEach((ds, i) => {
    config[ds.name] = { label: ds.name, color: CHART_COLORS[i % CHART_COLORS.length] }
  })
  return config
}

function toRechartsData(labels: string[], datasets: { name: string; values: number[] }[]) {
  return labels.map((label, i) => {
    const point: Record<string, string | number> = { label }
    datasets.forEach((ds) => { point[ds.name] = ds.values[i] ?? 0 })
    return point
  })
}

// ── App ───────────────────────────────────────────────────

export default function App() {
  const [data, setData] = useState<ReportData | null>(null)
  const [activeSection, setActiveSection] = useState("")

  useEffect(() => {
    fetch("./data.json")
      .then((r) => r.json())
      .then((d: ReportData) => {
        setData(d)
        if (d.sections.length > 0) setActiveSection(d.sections[0].id)
      })
      .catch(console.error)
  }, [])

  if (!data) return <div className="flex h-screen items-center justify-center">Loading...</div>

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        {/* Sidebar TOC */}
        <Sidebar className="border-r">
          <SidebarContent>
            <div className="p-4 border-b">
              <img src="./logo.png" alt="Logo" className="h-8 mb-2" onError={(e) => (e.currentTarget.style.display = "none")} />
              <div className="text-xs text-muted-foreground">{data.meta.firm}</div>
            </div>

            <SidebarGroup>
              <SidebarGroupLabel>Contents</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {data.sections.map((section) => (
                    <SidebarMenuItem key={section.id}>
                      <SidebarMenuButton
                        isActive={activeSection === section.id}
                        className={section.level > 1 ? "pl-6" : ""}
                        onClick={() => {
                          setActiveSection(section.id)
                          document.getElementById(section.id)?.scrollIntoView({ behavior: "smooth" })
                        }}
                      >
                        {section.heading}
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>

            {data.meta.sources && data.meta.sources.length > 0 && (
              <SidebarGroup>
                <SidebarGroupLabel>Sources</SidebarGroupLabel>
                <SidebarGroupContent>
                  <div className="px-3 text-xs text-muted-foreground space-y-1">
                    {data.meta.sources.map((src, i) => (
                      <div key={i} className="italic">{src}</div>
                    ))}
                  </div>
                </SidebarGroupContent>
              </SidebarGroup>
            )}
          </SidebarContent>
        </Sidebar>

        {/* Main content */}
        <div className="flex-1 flex flex-col">
          <header className="border-b px-6 py-4 flex items-center justify-between" style={{ backgroundColor: "var(--brand-primary)", color: "white" }}>
            <h1 className="text-xl font-bold">{data.meta.title}</h1>
            <span className="text-sm opacity-80">{new Date(data.meta.generated_at).toLocaleDateString()}</span>
          </header>

          <main className="flex-1 overflow-auto">
            <div className="max-w-3xl mx-auto p-6 space-y-8">
              {data.sections.map((section) => (
                <div key={section.id} id={section.id}>
                  {section.level === 1 ? (
                    <h2 className="text-2xl font-bold mb-3" style={{ color: "var(--brand-heading)" }}>{section.heading}</h2>
                  ) : section.level === 2 ? (
                    <h3 className="text-xl font-semibold mb-2" style={{ color: "var(--brand-heading)" }}>{section.heading}</h3>
                  ) : (
                    <h4 className="text-lg font-medium mb-2">{section.heading}</h4>
                  )}

                  <div className="prose prose-sm max-w-none text-muted-foreground whitespace-pre-wrap">
                    {section.content}
                  </div>

                  {/* Inline figures */}
                  {section.figures?.map((figure, fi) => (
                    <Card key={fi} className="mt-4">
                      <CardContent className="pt-6">
                        {figure.type === "chart" && figure.data.datasets && figure.data.labels && (
                          <FigureChart
                            type={figure.data.type || "bar"}
                            title={figure.data.title}
                            labels={figure.data.labels}
                            datasets={figure.data.datasets}
                          />
                        )}
                      </CardContent>
                    </Card>
                  ))}

                  <Separator className="mt-6" />
                </div>
              ))}
            </div>
          </main>

          <footer className="border-t px-6 py-3 text-xs text-muted-foreground flex justify-between">
            <span>{data.meta.confidential ? "CONFIDENTIAL — For internal use only." : ""}</span>
            <span>{data.meta.firm}</span>
          </footer>
        </div>
      </div>
    </SidebarProvider>
  )
}

// ── Figure chart renderer ─────────────────────────────────

function FigureChart({ type, title, labels, datasets }: {
  type: string
  title?: string
  labels: string[]
  datasets: { name: string; values: number[] }[]
}) {
  const config = buildChartConfig(datasets)
  const rechartsData = toRechartsData(labels, datasets)

  return (
    <div>
      {title && <h4 className="text-sm font-medium mb-2" style={{ color: "var(--brand-heading)" }}>{title}</h4>}
      <ChartContainer config={config} className="h-[250px] w-full">
        {type === "area" ? (
          <AreaChart data={rechartsData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--brand-border)" />
            <XAxis dataKey="label" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <ChartTooltip content={<ChartTooltipContent />} />
            {datasets.map((ds, i) => (
              <Area key={ds.name} type="monotone" dataKey={ds.name} stroke={CHART_COLORS[i]} fill={CHART_COLORS[i]} fillOpacity={0.15} strokeWidth={2} />
            ))}
          </AreaChart>
        ) : (
          <BarChart data={rechartsData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--brand-border)" />
            <XAxis dataKey="label" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <ChartLegend content={<ChartLegendContent />} />
            {datasets.map((ds, i) => (
              <Bar key={ds.name} dataKey={ds.name} fill={CHART_COLORS[i]} radius={[4, 4, 0, 0]} />
            ))}
          </BarChart>
        )}
      </ChartContainer>
    </div>
  )
}
