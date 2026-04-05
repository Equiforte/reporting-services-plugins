# shadcn/ui Component & Chart Reference

> **Source**: https://ui.shadcn.com  
> **Charts**: https://ui.shadcn.com/charts  
> **Blocks**: https://ui.shadcn.com/blocks  
> **MCP**: The shadcn MCP server is configured in `.mcp.json` — use it to look up component APIs and examples during builds.

All components use brand CSS custom properties for theming.

## Required shadcn/ui components

Installed during base template creation (`rebuild-base.sh`):

### Core UI

| Component | Source | Usage |
|-----------|--------|-------|
| `card` | [ui/card](https://ui.shadcn.com/docs/components/card) | KPI cards, content containers, comparison items |
| `table` | [ui/table](https://ui.shadcn.com/docs/components/table) | Data tables with branded headers |
| `badge` | [ui/badge](https://ui.shadcn.com/docs/components/badge) | Status labels, tags, confidence indicators, deltas |
| `tabs` | [ui/tabs](https://ui.shadcn.com/docs/components/tabs) | Section navigation, view switching, time period toggles |
| `separator` | [ui/separator](https://ui.shadcn.com/docs/components/separator) | Section dividers |
| `scroll-area` | [ui/scroll-area](https://ui.shadcn.com/docs/components/scroll-area) | Scrollable content regions |
| `collapsible` | [ui/collapsible](https://ui.shadcn.com/docs/components/collapsible) | Expandable timeline details, accordion sections |
| `tooltip` | [ui/tooltip](https://ui.shadcn.com/docs/components/tooltip) | Hover details on KPI deltas, chart points |
| `button` | [ui/button](https://ui.shadcn.com/docs/components/button) | Actions, export triggers |
| `select` | [ui/select](https://ui.shadcn.com/docs/components/select) | Filter dropdowns, time period selection |
| `dropdown-menu` | [ui/dropdown-menu](https://ui.shadcn.com/docs/components/dropdown-menu) | Context menus, export options |
| `avatar` | [ui/avatar](https://ui.shadcn.com/docs/components/avatar) | User/team indicators in headers |
| `breadcrumb` | [ui/breadcrumb](https://ui.shadcn.com/docs/components/breadcrumb) | Navigation hierarchy in report template |

### Charts (built on Recharts)

| Component | Source | Usage |
|-----------|--------|-------|
| `chart` | [ui/chart](https://ui.shadcn.com/docs/components/chart) | Base chart wrapper with theming and tooltip support |

The `chart` component from shadcn/ui provides `ChartContainer`, `ChartTooltip`, `ChartTooltipContent`, `ChartLegend`, and `ChartLegendContent`. It wraps Recharts and integrates with the shadcn theme system.

### Sidebar (block)

| Component | Source | Usage |
|-----------|--------|-------|
| `sidebar` | [ui/sidebar](https://ui.shadcn.com/docs/components/sidebar) | Report template TOC, dashboard navigation |

The sidebar component provides `SidebarProvider`, `Sidebar`, `SidebarContent`, `SidebarGroup`, `SidebarMenu`, `SidebarMenuItem`, `SidebarMenuButton`, and collapsible sections.

## Charts — detailed reference

> **Full docs**: https://ui.shadcn.com/charts  
> **Built on**: [Recharts](https://recharts.org/)

### Chart configuration

Define chart colors using brand tokens in a config object:

```tsx
import { type ChartConfig } from "@/components/ui/chart"

const chartConfig = {
  revenue: {
    label: "Revenue",
    color: "var(--brand-primary)",
  },
  expenses: {
    label: "Expenses",
    color: "var(--brand-accent)",
  },
  profit: {
    label: "Profit",
    color: "var(--brand-positive)",
  },
} satisfies ChartConfig
```

### Area Chart (https://ui.shadcn.com/charts/area)

Best for: revenue trends, growth over time, cumulative metrics.

```tsx
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

<ChartContainer config={chartConfig} className="h-[300px] w-full">
  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
    <CartesianGrid strokeDasharray="3 3" stroke="var(--brand-border)" />
    <XAxis dataKey="month" tick={{ fontSize: 12 }} />
    <YAxis tick={{ fontSize: 12 }} />
    <ChartTooltip content={<ChartTooltipContent />} />
    <Area
      type="monotone"
      dataKey="revenue"
      stroke="var(--brand-primary)"
      fill="var(--brand-primary)"
      fillOpacity={0.15}
      strokeWidth={2}
    />
  </AreaChart>
</ChartContainer>
```

**Stacked area** — for showing composition over time (e.g., revenue by segment):

```tsx
<Area type="monotone" dataKey="segment_a" stackId="1" stroke="var(--brand-primary)" fill="var(--brand-primary)" fillOpacity={0.3} />
<Area type="monotone" dataKey="segment_b" stackId="1" stroke="var(--brand-accent)" fill="var(--brand-accent)" fillOpacity={0.3} />
```

### Bar Chart (https://ui.shadcn.com/charts/bar)

Best for: comparisons across categories, quarterly revenue, budget vs actual.

```tsx
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from "@/components/ui/chart"

<ChartContainer config={chartConfig} className="h-[300px] w-full">
  <BarChart data={chartData}>
    <CartesianGrid strokeDasharray="3 3" stroke="var(--brand-border)" />
    <XAxis dataKey="quarter" tick={{ fontSize: 12 }} />
    <YAxis tick={{ fontSize: 12 }} />
    <ChartTooltip content={<ChartTooltipContent />} />
    <ChartLegend content={<ChartLegendContent />} />
    <Bar dataKey="revenue" fill="var(--brand-primary)" radius={[4, 4, 0, 0]} />
    <Bar dataKey="expenses" fill="var(--brand-accent)" radius={[4, 4, 0, 0]} />
  </BarChart>
</ChartContainer>
```

### Line Chart (https://ui.shadcn.com/charts/line)

Best for: trend lines, multiple metrics over time, performance tracking.

```tsx
import { Line, LineChart, CartesianGrid, XAxis, YAxis } from "recharts"

<ChartContainer config={chartConfig} className="h-[300px] w-full">
  <LineChart data={chartData}>
    <CartesianGrid strokeDasharray="3 3" stroke="var(--brand-border)" />
    <XAxis dataKey="month" tick={{ fontSize: 12 }} />
    <YAxis tick={{ fontSize: 12 }} />
    <ChartTooltip content={<ChartTooltipContent />} />
    <Line type="monotone" dataKey="revenue" stroke="var(--brand-primary)" strokeWidth={2} dot={{ r: 4 }} />
    <Line type="monotone" dataKey="target" stroke="var(--brand-accent)" strokeWidth={2} strokeDasharray="5 5" />
  </LineChart>
</ChartContainer>
```

### Pie / Donut Chart (https://ui.shadcn.com/charts/pie)

Best for: composition, market share, allocation breakdown.

```tsx
import { Pie, PieChart, Cell } from "recharts"

const COLORS = [
  "var(--brand-primary)",
  "var(--brand-accent)",
  "var(--brand-positive)",
  "var(--brand-warning)",
  "var(--brand-negative)",
]

<ChartContainer config={chartConfig} className="h-[300px] w-full">
  <PieChart>
    <ChartTooltip content={<ChartTooltipContent />} />
    <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={100}>
      {pieData.map((_, i) => (
        <Cell key={i} fill={COLORS[i % COLORS.length]} />
      ))}
    </Pie>
  </PieChart>
</ChartContainer>
```

### Radar Chart (https://ui.shadcn.com/charts/radar)

Best for: multi-dimensional comparison (product tiers, team performance).

```tsx
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from "recharts"

<ChartContainer config={chartConfig} className="h-[300px] w-full">
  <RadarChart data={radarData}>
    <PolarGrid stroke="var(--brand-border)" />
    <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 11 }} />
    <PolarRadiusAxis tick={{ fontSize: 10 }} />
    <Radar name="Product A" dataKey="a" stroke="var(--brand-primary)" fill="var(--brand-primary)" fillOpacity={0.2} />
    <Radar name="Product B" dataKey="b" stroke="var(--brand-accent)" fill="var(--brand-accent)" fillOpacity={0.2} />
  </RadarChart>
</ChartContainer>
```

### Chart selection guide

| Data type | Recommended chart | shadcn/Recharts |
|-----------|------------------|-----------------|
| Trend over time | Area chart | `AreaChart` + `Area` |
| Category comparison | Bar chart | `BarChart` + `Bar` |
| Multiple trends | Line chart | `LineChart` + `Line` |
| Composition / share | Pie or donut | `PieChart` + `Pie` |
| Multi-axis comparison | Radar | `RadarChart` + `Radar` |
| Quarterly financials | Grouped bar | `BarChart` + multiple `Bar` |
| Budget vs actual | Stacked bar | `BarChart` + `Bar` with `stackId` |
| Growth trajectory | Area (filled) | `AreaChart` + `Area` with `fillOpacity` |

## Sidebar — detailed reference

> **Full docs**: https://ui.shadcn.com/docs/components/sidebar  
> **Blocks**: https://ui.shadcn.com/blocks

Use the sidebar for the **report** template's table of contents and the **dashboard** template's optional navigation.

### Report sidebar (TOC)

```tsx
import {
  Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent,
  SidebarGroupLabel, SidebarMenu, SidebarMenuItem, SidebarMenuButton,
  SidebarProvider,
} from "@/components/ui/sidebar"

<SidebarProvider>
  <Sidebar>
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>Contents</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            {sections.map((section) => (
              <SidebarMenuItem key={section.id}>
                <SidebarMenuButton asChild isActive={activeSection === section.id}>
                  <a href={`#${section.id}`}>{section.heading}</a>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
  </Sidebar>
  <main>{/* content */}</main>
</SidebarProvider>
```

### Dashboard sidebar (optional, for multi-page dashboards)

```tsx
<Sidebar>
  <SidebarContent>
    <SidebarGroup>
      <SidebarGroupLabel>Views</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton isActive={view === "overview"} onClick={() => setView("overview")}>
              Overview
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton isActive={view === "financials"} onClick={() => setView("financials")}>
              Financials
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  </SidebarContent>
</Sidebar>
```

## Component patterns

### KPI Card

```tsx
<Card style={{ borderRadius: 'var(--brand-card-radius)', boxShadow: 'var(--brand-card-shadow)' }}>
  <CardContent className="p-4">
    <div className="text-2xl font-bold" style={{ color: 'var(--brand-primary)' }}>
      {kpi.value}
    </div>
    <div className="text-sm text-muted-foreground">{kpi.label}</div>
    {kpi.delta && (
      <Badge variant={kpi.trend === 'up' ? 'default' : 'destructive'} className="mt-1">
        {kpi.delta}
      </Badge>
    )}
  </CardContent>
</Card>
```

### Data Table

```tsx
<Table>
  <TableHeader>
    <TableRow style={{ backgroundColor: 'var(--brand-primary)' }}>
      {columns.map(col => (
        <TableHead key={col.key} className={`text-white ${col.align === 'right' ? 'text-right' : ''}`}>
          {col.label}
        </TableHead>
      ))}
    </TableRow>
  </TableHeader>
  <TableBody>
    {rows.map((row, i) => (
      <TableRow key={i} className={i % 2 === 0 ? '' : 'bg-muted/50'}>
        {columns.map(col => (
          <TableCell key={col.key} className={col.align === 'right' ? 'text-right' : ''}>
            {formatValue(row[col.key], col.format)}
          </TableCell>
        ))}
      </TableRow>
    ))}
  </TableBody>
</Table>
```

### Comparison Card

```tsx
<Card className={cn("p-6", item.highlighted && "ring-2 ring-primary")}>
  <CardHeader>
    <CardTitle>{item.name}</CardTitle>
    {item.subtitle && <CardDescription>{item.subtitle}</CardDescription>}
  </CardHeader>
  <CardContent>
    {Object.entries(item.attributes).map(([key, attr]) => (
      <div key={key} className="flex justify-between py-2 border-b">
        <span className="text-muted-foreground">{attributeLabels[key]}</span>
        <span className="font-medium">{attr.value}</span>
      </div>
    ))}
  </CardContent>
</Card>
```

### Timeline Event

```tsx
<div className="flex gap-4">
  <div className="flex flex-col items-center">
    <div className={cn("w-3 h-3 rounded-full", statusColorClass)} />
    <div className="w-px flex-1 bg-border" />
  </div>
  <Collapsible>
    <CollapsibleTrigger>
      <div className="font-medium">{event.title}</div>
      <div className="text-sm text-muted-foreground">{event.date}</div>
    </CollapsibleTrigger>
    <CollapsibleContent>
      <p>{event.description}</p>
    </CollapsibleContent>
  </Collapsible>
</div>
```

## Layout patterns

### Dashboard layout (with optional sidebar)
```
┌──────┬──────────────────────────────┐
│      │ Header (logo + title + date) │
│ Side │─────────────────────────────── │
│ bar  │ KPI 1  │ KPI 2 │ KPI 3 │KPI4│
│(opt) │─────────────────────────────── │
│      │ Area Chart (revenue trend)   │
│      │─────────────────────────────── │
│      │ Bar Chart │ Pie Chart        │
│      │─────────────────────────────── │
│      │ Data table                   │
│      │─────────────────────────────── │
│      │ Footer                       │
└──────┴──────────────────────────────┘
```

### Report layout (with sidebar TOC)
```
┌──────┬──────────────────────────┐
│ Side │ Section 1                │
│ bar  │  ├─ Content              │
│ TOC  │  └─ Area Chart           │
│      ├──────────────────────────┤
│      │ Section 2                │
│      │  ├─ Content              │
│      │  └─ Bar Chart + Table    │
├──────┴──────────────────────────┤
│ Footer                          │
└─────────────────────────────────┘
```

### Comparison layout
```
┌─────────────────────────────────┐
│ Header + title                  │
├──────────┬──────────┬───────────┤
│ Item 1   │ Item 2   │ Item 3    │
│ (card)   │ (card)   │ (card)    │
│          │highlighted│           │
├─────────────────────────────────┤
│ Radar Chart (multi-axis)        │
├─────────────────────────────────┤
│ Footer                          │
└─────────────────────────────────┘
```

### Timeline layout
```
┌─────────────────────────────────┐
│ Header + title                  │
├─────────────────────────────────┤
│ ● Event 1 (completed)          │
│ │  └─ Details (collapsible)    │
│ ● Event 2 (in-progress)        │
│ │  └─ Details                  │
│ ○ Event 3 (upcoming)           │
│    └─ Details                  │
├─────────────────────────────────┤
│ Footer                          │
└─────────────────────────────────┘
```
