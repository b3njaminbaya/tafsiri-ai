import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { api, ApiError, type AnalyticsSummary } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const BRAND = "hsl(var(--brand))";
const GRID = "hsl(var(--border))";
const AXIS_TEXT = "hsl(var(--muted-foreground))";

function ChartTooltip({ active, payload, label, unit }: { active?: boolean; payload?: { value: number }[]; label?: string; unit?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border bg-popover px-3 py-2 text-sm shadow-md">
      <div className="text-muted-foreground text-xs mb-1">{label}</div>
      <div className="font-medium">{payload[0].value}{unit}</div>
    </div>
  );
}

const StatTile = ({ label, value }: { label: string; value: string }) => (
  <div className="rounded-lg border bg-card p-4">
    <div className="text-2xl font-bold tabular-nums">{value}</div>
    <div className="text-sm text-muted-foreground mt-1">{label}</div>
  </div>
);

const Analytics = () => {
  const { token, isLoading: authLoading } = useAuth();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    api
      .getAnalyticsSummary(token)
      .then(setSummary)
      .catch((err) => {
        const description = err instanceof ApiError ? err.message : String(err);
        toast({ title: "Failed to load analytics", description });
      })
      .finally(() => setLoading(false));
  }, [token]);

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center py-24 text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin mr-2" />
        Loading analytics...
      </div>
    );
  }

  const totalFeedback = summary?.feedback_breakdown.reduce((sum, r) => sum + r.count, 0) ?? 0;
  const ratingData = [1, 2, 3, 4, 5].map((rating) => ({
    rating: `${rating}★`,
    count: summary?.feedback_breakdown.find((r) => r.rating === rating)?.count ?? 0,
  }));
  const pairData = (summary?.top_language_pairs ?? []).map((p) => ({
    pair: `${p.source_lang ?? "auto"} → ${p.target_lang}`,
    count: p.count,
  }));

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-4">Your Translation Analytics</h1>
        <p className="text-xl text-muted-foreground max-w-3xl">
          A real accounting of your own usage — every number here comes from your saved
          translation history, not a mockup.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        <StatTile label="Translations" value={String(summary?.total_translations ?? 0)} />
        <StatTile
          label="Avg. confidence"
          value={`${((summary?.average_confidence ?? 0) * 100).toFixed(0)}%`}
        />
        <StatTile label="Language pairs used" value={String(pairData.length)} />
        <StatTile label="Feedback given" value={String(totalFeedback)} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Translations over time</CardTitle>
            <CardDescription>Daily translation volume</CardDescription>
          </CardHeader>
          <CardContent>
            {summary && summary.translations_by_day.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart data={summary.translations_by_day} margin={{ left: -20 }}>
                  <defs>
                    <linearGradient id="translationsFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={BRAND} stopOpacity={0.35} />
                      <stop offset="100%" stopColor={BRAND} stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid vertical={false} stroke={GRID} strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tick={{ fill: AXIS_TEXT, fontSize: 12 }}
                    axisLine={{ stroke: GRID }}
                    tickLine={false}
                  />
                  <YAxis
                    allowDecimals={false}
                    tick={{ fill: AXIS_TEXT, fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                    width={30}
                  />
                  <Tooltip content={<ChartTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke={BRAND}
                    strokeWidth={2}
                    fill="url(#translationsFill)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-muted-foreground py-16 text-center">
                Translate something to see your activity here.
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Top language pairs</CardTitle>
            <CardDescription>Most-used source → target combinations</CardDescription>
          </CardHeader>
          <CardContent>
            {pairData.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={pairData} layout="vertical" margin={{ left: 10 }}>
                  <CartesianGrid horizontal={false} stroke={GRID} strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    allowDecimals={false}
                    tick={{ fill: AXIS_TEXT, fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    dataKey="pair"
                    type="category"
                    tick={{ fill: AXIS_TEXT, fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                    width={90}
                  />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: "hsl(var(--muted))" }} />
                  <Bar dataKey="count" fill={BRAND} radius={[0, 4, 4, 0]} maxBarSize={22} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-muted-foreground py-16 text-center">
                No translations yet.
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">Feedback ratings</CardTitle>
            <CardDescription>How you've rated your own translations</CardDescription>
          </CardHeader>
          <CardContent>
            {totalFeedback > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={ratingData} margin={{ left: -20 }}>
                  <CartesianGrid vertical={false} stroke={GRID} strokeDasharray="3 3" />
                  <XAxis
                    dataKey="rating"
                    tick={{ fill: AXIS_TEXT, fontSize: 12 }}
                    axisLine={{ stroke: GRID }}
                    tickLine={false}
                  />
                  <YAxis
                    allowDecimals={false}
                    tick={{ fill: AXIS_TEXT, fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                    width={30}
                  />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: "hsl(var(--muted))" }} />
                  <Bar dataKey="count" fill={BRAND} radius={[4, 4, 0, 0]} maxBarSize={48} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-muted-foreground py-16 text-center">
                Rate a translation on the Translate page to see feedback trends here.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Analytics;
