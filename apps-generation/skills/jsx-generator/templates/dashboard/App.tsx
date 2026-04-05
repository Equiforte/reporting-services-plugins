import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent,
  SidebarGroupLabel, SidebarHeader, SidebarInset, SidebarMenu, SidebarMenuItem,
  SidebarMenuButton, SidebarMenuSub, SidebarMenuSubItem, SidebarMenuSubButton,
  SidebarProvider, SidebarRail, SidebarTrigger,
} from "@/components/ui/sidebar"
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from "@/components/ui/chart"
import { Area, AreaChart, Bar, BarChart, CartesianGrid, XAxis, YAxis, Pie, PieChart, Cell } from "recharts"
import type { ChartConfig } from "@/components/ui/chart"

// ── Types ──────────────────────────────────────────────────

interface KPI {
  label: string
  value: string
  raw_value?: number
  delta?: string
  trend?: "up" | "down" | "flat"
  unit?: string
}

interface ChartDataset {
  name: string
  values: number[]
}

interface ChartData {
  type: "area" | "bar" | "line" | "pie" | "doughnut"
  title: string
  labels: string[]
  datasets: ChartDataset[]
}

interface TableColumn {
  key: string
  label: string
  align?: "left" | "right" | "center"
  format?: "currency" | "percentage" | "integer"
}

interface TableData {
  title: string
  columns: TableColumn[]
  rows: Record<string, string | number>[]
}

interface DashboardData {
  meta: {
    title: string
    generated_at: string
    confidential: boolean
    firm?: string
    sources?: string[]
  }
  kpis: KPI[]
  charts: ChartData[]
  tables: TableData[]
}

// ── Helpers ────────────────────────────────────────────────

const CHART_COLORS = [
  "var(--brand-primary)",
  "var(--brand-accent)",
  "var(--brand-positive)",
  "var(--brand-warning)",
  "var(--brand-negative)",
]

function buildChartConfig(datasets: ChartDataset[]): ChartConfig {
  const config: ChartConfig = {}
  datasets.forEach((ds, i) => {
    config[ds.name] = { label: ds.name, color: CHART_COLORS[i % CHART_COLORS.length] }
  })
  return config
}

function toRechartsData(labels: string[], datasets: ChartDataset[]) {
  return labels.map((label, i) => {
    const point: Record<string, string | number> = { label }
    datasets.forEach((ds) => { point[ds.name] = ds.values[i] ?? 0 })
    return point
  })
}

function formatValue(val: string | number | undefined, format?: string): string {
  if (val === undefined || val === null) return ""
  const num = typeof val === "string" ? parseFloat(val) : val
  if (isNaN(num)) return String(val)
  switch (format) {
    case "currency": return `$${num.toLocaleString()}`
    case "percentage": return `${num.toFixed(1)}%`
    case "integer": return num.toLocaleString()
    default: return String(val)
  }
}

// ── SVG Icons (inline to avoid external deps) ─────────────

const IconDashboard = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="7" height="9" x="3" y="3" rx="1" /><rect width="7" height="5" x="14" y="3" rx="1" /><rect width="7" height="9" x="14" y="12" rx="1" /><rect width="7" height="5" x="3" y="16" rx="1" />
  </svg>
)

const IconSettings = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
)

const IconBarChart = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" x2="12" y1="20" y2="10" /><line x1="18" x2="18" y1="20" y2="4" /><line x1="6" x2="6" y1="20" y2="16" />
  </svg>
)

const IconTable = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3v18" /><rect width="18" height="18" x="3" y="3" rx="2" /><path d="M3 9h18" /><path d="M3 15h18" />
  </svg>
)

// ── App ───────────────────────────────────────────────────

type Page = "dashboard" | "settings"

export default function App() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [page, setPage] = useState<Page>("dashboard")
  const [dashboardSection, setDashboardSection] = useState("overview")

  useEffect(() => {
    fetch("./data.json")
      .then((r) => r.json())
      .then(setData)
      .catch(console.error)
  }, [])

  if (!data) return <div className="flex h-screen items-center justify-center">Loading...</div>

  return (
    <SidebarProvider>
      {/* ── Sidebar ── */}
      <Sidebar collapsible="icon">
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="lg" asChild>
                <a href="#">
                  <div className="flex aspect-square size-8 items-center justify-center rounded-lg" style={{ backgroundColor: "var(--brand-primary)", color: "white" }}>
                    <img src="./logo.png" alt="" className="size-5" onError={(e) => { e.currentTarget.style.display = "none"; e.currentTarget.parentElement!.textContent = data.meta.firm?.charAt(0) || "D" }} />
                  </div>
                  <div className="flex flex-col gap-0.5 leading-none">
                    <span className="font-semibold text-sm">{data.meta.firm}</span>
                    <span className="text-xs text-muted-foreground">{data.meta.title}</span>
                  </div>
                </a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>

        <SidebarContent>
          {/* Primary nav: Dashboard + Settings */}
          <SidebarGroup>
            <SidebarGroupLabel>Platform</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {/* Dashboard — with sub-items for sections */}
                <SidebarMenuItem>
                  <SidebarMenuButton isActive={page === "dashboard"} onClick={() => setPage("dashboard")}>
                    <IconDashboard />
                    <span>Dashboard</span>
                  </SidebarMenuButton>
                  {page === "dashboard" && (
                    <SidebarMenuSub>
                      {[
                        { id: "overview", label: "Overview", icon: <IconDashboard /> },
                        { id: "charts", label: "Charts", icon: <IconBarChart /> },
                        { id: "data", label: "Data", icon: <IconTable /> },
                      ].map((item) => (
                        <SidebarMenuSubItem key={item.id}>
                          <SidebarMenuSubButton
                            isActive={dashboardSection === item.id}
                            onClick={() => {
                              setDashboardSection(item.id)
                              document.getElementById(item.id)?.scrollIntoView({ behavior: "smooth" })
                            }}
                          >
                            {item.icon}
                            <span>{item.label}</span>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      ))}
                    </SidebarMenuSub>
                  )}
                </SidebarMenuItem>

                {/* Settings */}
                <SidebarMenuItem>
                  <SidebarMenuButton isActive={page === "settings"} onClick={() => setPage("settings")}>
                    <IconSettings />
                    <span>Settings</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>

          {/* Sources */}
          {data.meta.sources && data.meta.sources.length > 0 && (
            <SidebarGroup>
              <SidebarGroupLabel>Data Sources</SidebarGroupLabel>
              <SidebarGroupContent>
                <div className="px-3 text-xs text-muted-foreground space-y-1">
                  {data.meta.sources.map((src, i) => (
                    <div key={i} className="truncate">{src}</div>
                  ))}
                </div>
              </SidebarGroupContent>
            </SidebarGroup>
          )}
        </SidebarContent>

        <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="sm">
                <span className="text-xs text-muted-foreground">{data.meta.confidential ? "CONFIDENTIAL" : ""}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>

        <SidebarRail />
      </Sidebar>

      {/* ── Main content (SidebarInset) ── */}
      <SidebarInset>
        {/* Header with SidebarTrigger */}
        <header className="flex h-14 items-center gap-4 border-b px-6" style={{ backgroundColor: "var(--brand-primary)", color: "white" }}>
          <SidebarTrigger className="text-white hover:bg-white/10 -ml-1" />
          <div className="flex-1 flex items-center justify-between">
            <h1 className="text-lg font-semibold">{page === "dashboard" ? data.meta.title : "Settings"}</h1>
            <span className="text-sm opacity-80">{new Date(data.meta.generated_at).toLocaleDateString()}</span>
          </div>
        </header>

        {/* Page content */}
        {page === "dashboard" ? (
          <DashboardPage data={data} />
        ) : (
          <SettingsPage data={data} />
        )}
      </SidebarInset>
    </SidebarProvider>
  )
}

// ── Dashboard page ────────────────────────────────────────

function DashboardPage({ data }: { data: DashboardData }) {
  return (
    <main className="flex-1 overflow-auto p-6 space-y-8">
      {/* Overview: KPI Cards */}
      <section id="overview">
        <h2 className="text-lg font-semibold mb-4" style={{ color: "var(--brand-heading)" }}>Key Metrics</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {data.kpis.map((kpi, i) => (
            <Card key={i} style={{ borderRadius: "var(--brand-card-radius)", boxShadow: "var(--brand-card-shadow)" }}>
              <CardContent className="p-4">
                <div className="text-sm text-muted-foreground mb-1">{kpi.label}</div>
                <div className="text-2xl font-bold" style={{ color: "var(--brand-primary)" }}>{kpi.value}</div>
                {kpi.delta && (
                  <Badge variant={kpi.trend === "up" ? "default" : kpi.trend === "down" ? "destructive" : "secondary"} className="mt-2">
                    {kpi.delta}
                  </Badge>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Charts */}
      {data.charts.length > 0 && (
        <section id="charts">
          <h2 className="text-lg font-semibold mb-4" style={{ color: "var(--brand-heading)" }}>Charts</h2>
          {data.charts.length > 1 ? (
            <Tabs defaultValue={data.charts[0].title}>
              <TabsList>
                {data.charts.map((chart) => (
                  <TabsTrigger key={chart.title} value={chart.title}>{chart.title}</TabsTrigger>
                ))}
              </TabsList>
              {data.charts.map((chart) => (
                <TabsContent key={chart.title} value={chart.title}>
                  <Card><CardContent className="pt-6"><ChartBlock chart={chart} /></CardContent></Card>
                </TabsContent>
              ))}
            </Tabs>
          ) : (
            <Card><CardContent className="pt-6"><ChartBlock chart={data.charts[0]} /></CardContent></Card>
          )}
        </section>
      )}

      {/* Data Tables */}
      {data.tables.length > 0 && (
        <section id="data">
          <h2 className="text-lg font-semibold mb-4" style={{ color: "var(--brand-heading)" }}>Data</h2>
          {data.tables.map((table, i) => (
            <div key={i} className="mb-6">
              <h3 className="text-md font-medium mb-2">{table.title}</h3>
              <Card>
                <Table>
                  <TableHeader>
                    <TableRow style={{ backgroundColor: "var(--brand-primary)" }}>
                      {table.columns.map((col) => (
                        <TableHead key={col.key} className={`text-white ${col.align === "right" ? "text-right" : ""}`}>
                          {col.label}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {table.rows.map((row, j) => (
                      <TableRow key={j} className={j % 2 === 1 ? "bg-muted/50" : ""}>
                        {table.columns.map((col) => (
                          <TableCell key={col.key} className={col.align === "right" ? "text-right" : ""}>
                            {formatValue(row[col.key], col.format)}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Card>
            </div>
          ))}
        </section>
      )}
    </main>
  )
}

// ── Settings page ─────────────────────────────────────────

function SettingsPage({ data }: { data: DashboardData }) {
  return (
    <main className="flex-1 overflow-auto p-6 space-y-6">
      <h2 className="text-lg font-semibold" style={{ color: "var(--brand-heading)" }}>Dashboard Settings</h2>

      <Card>
        <CardContent className="p-6 space-y-4">
          <h3 className="font-medium">Report Information</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-muted-foreground">Title</div>
              <div className="font-medium">{data.meta.title}</div>
            </div>
            <div>
              <div className="text-muted-foreground">Generated</div>
              <div className="font-medium">{new Date(data.meta.generated_at).toLocaleString()}</div>
            </div>
            <div>
              <div className="text-muted-foreground">Organization</div>
              <div className="font-medium">{data.meta.firm}</div>
            </div>
            <div>
              <div className="text-muted-foreground">Classification</div>
              <div className="font-medium">{data.meta.confidential ? "Confidential" : "Public"}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {data.meta.sources && data.meta.sources.length > 0 && (
        <Card>
          <CardContent className="p-6 space-y-4">
            <h3 className="font-medium">Data Sources</h3>
            <div className="space-y-2">
              {data.meta.sources.map((src, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: "var(--brand-accent)" }} />
                  {src}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="p-6 space-y-4">
          <h3 className="font-medium">Dashboard Contents</h3>
          <div className="text-sm text-muted-foreground space-y-1">
            <div>{data.kpis.length} KPI metrics</div>
            <div>{data.charts.length} charts</div>
            <div>{data.tables.length} data tables</div>
          </div>
        </CardContent>
      </Card>
    </main>
  )
}

// ── Chart renderer ────────────────────────────────────────

function ChartBlock({ chart }: { chart: ChartData }) {
  const config = buildChartConfig(chart.datasets)
  const rechartsData = toRechartsData(chart.labels, chart.datasets)

  if (chart.type === "area") {
    return (
      <ChartContainer config={config} className="h-[300px] w-full">
        <AreaChart data={rechartsData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--brand-border)" />
          <XAxis dataKey="label" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <ChartTooltip content={<ChartTooltipContent />} />
          <ChartLegend content={<ChartLegendContent />} />
          {chart.datasets.map((ds, i) => (
            <Area key={ds.name} type="monotone" dataKey={ds.name} stroke={CHART_COLORS[i % CHART_COLORS.length]} fill={CHART_COLORS[i % CHART_COLORS.length]} fillOpacity={0.15} strokeWidth={2} />
          ))}
        </AreaChart>
      </ChartContainer>
    )
  }

  if (chart.type === "bar") {
    return (
      <ChartContainer config={config} className="h-[300px] w-full">
        <BarChart data={rechartsData}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--brand-border)" />
          <XAxis dataKey="label" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <ChartTooltip content={<ChartTooltipContent />} />
          <ChartLegend content={<ChartLegendContent />} />
          {chart.datasets.map((ds, i) => (
            <Bar key={ds.name} dataKey={ds.name} fill={CHART_COLORS[i % CHART_COLORS.length]} radius={[4, 4, 0, 0]} />
          ))}
        </BarChart>
      </ChartContainer>
    )
  }

  if (chart.type === "pie" || chart.type === "doughnut") {
    const pieData = chart.labels.map((label, i) => ({
      name: label,
      value: chart.datasets[0]?.values[i] ?? 0,
    }))
    return (
      <ChartContainer config={config} className="h-[300px] w-full">
        <PieChart>
          <ChartTooltip content={<ChartTooltipContent />} />
          <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={chart.type === "doughnut" ? 60 : 0} outerRadius={100}>
            {pieData.map((_, i) => (
              <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
            ))}
          </Pie>
        </PieChart>
      </ChartContainer>
    )
  }

  // Fallback: bar
  return (
    <ChartContainer config={config} className="h-[300px] w-full">
      <BarChart data={rechartsData}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--brand-border)" />
        <XAxis dataKey="label" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <ChartTooltip content={<ChartTooltipContent />} />
        {chart.datasets.map((ds, i) => (
          <Bar key={ds.name} dataKey={ds.name} fill={CHART_COLORS[i % CHART_COLORS.length]} radius={[4, 4, 0, 0]} />
        ))}
      </BarChart>
    </ChartContainer>
  )
}
