import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, ShieldAlert, CheckCircle2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { api, ApiError, type TranslationRecord } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const Review = () => {
  const { token, user, isLoading: authLoading } = useAuth();
  const [queue, setQueue] = useState<TranslationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [drafts, setDrafts] = useState<Record<number, string>>({});
  const [submitting, setSubmitting] = useState<number | null>(null);

  const canReview = user?.role?.name === "translator" || user?.role?.name === "admin";

  const loadQueue = async () => {
    if (!token) return;
    try {
      setLoading(true);
      const data = await api.getReviewQueue(token);
      setQueue(data);
    } catch (err) {
      const description = err instanceof ApiError ? err.message : String(err);
      toast({ title: "Failed to load review queue", description });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (canReview) loadQueue();
    else setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, canReview]);

  const submitCorrection = async (translationId: number) => {
    if (!token) return;
    const correctedText = drafts[translationId]?.trim();
    if (!correctedText) {
      toast({ title: "Enter a corrected translation first" });
      return;
    }
    try {
      setSubmitting(translationId);
      await api.submitCorrection(translationId, { corrected_text: correctedText }, token);
      toast({ title: "Correction submitted" });
      setQueue((prev) => prev.filter((t) => t.id !== translationId));
    } catch (err) {
      const description = err instanceof ApiError ? err.message : String(err);
      toast({ title: "Failed to submit correction", description });
    } finally {
      setSubmitting(null);
    }
  };

  if (authLoading) return null;

  if (!canReview) {
    return (
      <div className="container mx-auto px-4 py-24 text-center">
        <ShieldAlert className="h-10 w-10 mx-auto mb-4 text-muted-foreground" />
        <h1 className="text-2xl font-bold mb-2">Reviewer access required</h1>
        <p className="text-muted-foreground max-w-md mx-auto">
          The review queue is available to translator and admin accounts. Ask an
          admin to promote your account if you should have access.
        </p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-4">Review Queue</h1>
        <p className="text-xl text-muted-foreground max-w-3xl">
          Low-confidence translations awaiting a human correction — the active-learning
          loop that turns real usage into training signal.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-24 text-muted-foreground">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          Loading queue...
        </div>
      ) : queue.length === 0 ? (
        <div className="text-center py-24 text-muted-foreground">
          <CheckCircle2 className="h-10 w-10 mx-auto mb-4" />
          Nothing needs review right now.
        </div>
      ) : (
        <div className="space-y-6 max-w-3xl">
          {queue.map((t) => (
            <Card key={t.id}>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-base font-medium">
                  {t.source_lang ?? "auto"} → {t.target_lang}
                  {t.domain && <Badge variant="outline" className="ml-2">{t.domain}</Badge>}
                </CardTitle>
                <Badge variant="destructive">{(t.confidence * 100).toFixed(0)}% confidence</Badge>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Source text</p>
                  <p className="text-sm">{t.input_text}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Model output</p>
                  <p className="text-sm">{t.output_text}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Your correction</p>
                  <Textarea
                    value={drafts[t.id] ?? ""}
                    onChange={(e) => setDrafts((prev) => ({ ...prev, [t.id]: e.target.value }))}
                    placeholder="Enter the correct translation..."
                    rows={2}
                  />
                </div>
                <div className="flex justify-end">
                  <Button
                    size="sm"
                    onClick={() => submitCorrection(t.id)}
                    disabled={submitting === t.id}
                  >
                    {submitting === t.id ? "Submitting..." : "Submit correction"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Review;
