import { useCallback, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle, AlertCircle, XCircle, Loader2, RefreshCw, Database, Server, Cpu, HardDrive } from "lucide-react";
import { api, ApiError, type SystemStatus as SystemStatusData } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const DEPENDENCY_META: Record<string, { label: string; icon: JSX.Element }> = {
  database: { label: "Database", icon: <Database className="h-5 w-5" /> },
  cache: { label: "Cache", icon: <Server className="h-5 w-5" /> },
  storage: { label: "Dataset Storage", icon: <HardDrive className="h-5 w-5" /> },
  translation_model: { label: "Translation Model", icon: <Cpu className="h-5 w-5" /> },
};

function statusIcon(status: string) {
  switch (status) {
    case "operational":
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    case "degraded":
      return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    default:
      return <XCircle className="h-4 w-4 text-red-500" />;
  }
}

function statusBadge(status: string) {
  switch (status) {
    case "operational":
      return <Badge className="bg-green-100 text-green-800 border-green-200">Operational</Badge>;
    case "degraded":
      return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">Degraded</Badge>;
    default:
      return <Badge className="bg-red-100 text-red-800 border-red-200">Down</Badge>;
  }
}

const SystemStatus = () => {
  const [data, setData] = useState<SystemStatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      const status = await api.getSystemStatus();
      setData(status);
    } catch (err) {
      const description = err instanceof ApiError ? err.message : String(err);
      toast({ title: "Failed to load status", description });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">System Status</h1>
        {loading ? (
          <div className="flex items-center justify-center gap-2 mb-4 text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin" /> Checking live status...
          </div>
        ) : data ? (
          <div className="flex items-center justify-center gap-2 mb-4">
            {statusIcon(data.status)}
            <span className="text-xl capitalize">
              {data.status === "operational" ? "All Systems Operational" : `Status: ${data.status}`}
            </span>
          </div>
        ) : (
          <div className="flex items-center justify-center gap-2 mb-4 text-muted-foreground">
            <XCircle className="h-5 w-5 text-red-500" /> Could not reach the status endpoint
          </div>
        )}
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Live status of the backend and every service it depends on — checked fresh on every load,
          not a fixed page.
        </p>
        {data && (
          <p className="text-xs text-muted-foreground mt-2">
            Last checked: {new Date(data.checked_at).toLocaleString()}
          </p>
        )}
        <Button
          variant="outline"
          size="sm"
          className="mt-4"
          onClick={() => load(true)}
          disabled={refreshing}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
          {refreshing ? "Refreshing..." : "Refresh"}
        </Button>
      </div>

      {data && (
        <div>
          <h2 className="text-2xl font-bold mb-6">Service Status</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {Object.entries(data.dependencies).map(([key, dep]) => {
              const meta = DEPENDENCY_META[key] ?? { label: key, icon: <Server className="h-5 w-5" /> };
              return (
                <Card key={key}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="text-primary">{meta.icon}</div>
                        <CardTitle className="text-lg">{meta.label}</CardTitle>
                      </div>
                      {statusBadge(dep.status)}
                    </div>
                  </CardHeader>
                  {dep.detail && (
                    <CardContent>
                      <p className="text-sm text-muted-foreground">{dep.detail}</p>
                    </CardContent>
                  )}
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemStatus;
