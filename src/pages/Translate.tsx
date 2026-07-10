import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { toast } from "@/hooks/use-toast";
import { Languages, ArrowRight, Copy, Volume2, RotateCcw, Sparkles, Clock, CheckCircle, ThumbsUp, ThumbsDown } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { api, ApiError } from "@/lib/api";

const Translate = () => {
  const { token } = useAuth();
  const [text, setText] = useState("");
  const [sourceLanguage, setSourceLanguage] = useState("auto");
  const [targetLanguage, setTargetLanguage] = useState("en");
  const [domain, setDomain] = useState<string | undefined>(undefined);
  const [output, setOutput] = useState<string>("");
  const [confidence, setConfidence] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [detectedLanguage, setDetectedLanguage] = useState<string | null>(null);
  const [translationId, setTranslationId] = useState<number | null>(null);
  const [feedbackRating, setFeedbackRating] = useState<number | null>(null);
  const [submittingFeedback, setSubmittingFeedback] = useState(false);

  const commonLanguages = [
    { code: "auto", name: "Auto-detect", flag: "🌐" },
    { code: "en", name: "English", flag: "🇺🇸" },
    { code: "es", name: "Spanish", flag: "🇪🇸" },
    { code: "fr", name: "French", flag: "🇫🇷" },
    { code: "de", name: "German", flag: "🇩🇪" },
    { code: "it", name: "Italian", flag: "🇮🇹" },
    { code: "pt", name: "Portuguese", flag: "🇵🇹" },
    { code: "ru", name: "Russian", flag: "🇷🇺" },
    { code: "ja", name: "Japanese", flag: "🇯🇵" },
    { code: "ko", name: "Korean", flag: "🇰🇷" },
    { code: "zh", name: "Chinese", flag: "🇨🇳" },
    { code: "ar", name: "Arabic", flag: "🇸🇦" },
    { code: "hi", name: "Hindi", flag: "🇮🇳" },
    { code: "sw", name: "Swahili", flag: "🇹🇿" },
    { code: "am", name: "Amharic", flag: "🇪🇹" },
    { code: "ha", name: "Hausa", flag: "🇳🇬" },
    { code: "ig", name: "Igbo", flag: "🇳🇬" },
    { code: "yo", name: "Yoruba", flag: "🇳🇬" },
    { code: "zu", name: "Zulu", flag: "🇿🇦" },
    { code: "xh", name: "Xhosa", flag: "🇿🇦" },
    { code: "so", name: "Somali", flag: "🇸🇴" },
    { code: "ln", name: "Lingala", flag: "🇨🇩" },
    { code: "wo", name: "Wolof", flag: "🇸🇳" },
    { code: "ff", name: "Fulah", flag: "🇸🇳" },
    { code: "lg", name: "Ganda", flag: "🇺🇬" },
  ];

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({ title: "Copied to clipboard!" });
    } catch (err) {
      toast({ title: "Failed to copy", description: "Please try again" });
    }
  };

  const swapLanguages = () => {
    if (sourceLanguage !== "auto") {
      setSourceLanguage(targetLanguage);
      setTargetLanguage(sourceLanguage);
      setText(output);
      setOutput(text);
    }
  };

  const clearAll = () => {
    setText("");
    setOutput("");
    setConfidence(null);
    setDetectedLanguage(null);
    setTranslationId(null);
    setFeedbackRating(null);
  };

  const runTranslate = async () => {
    if (!token) {
      toast({ title: "Please log in" });
      return;
    }
    try {
      setLoading(true);
      setFeedbackRating(null);
      const data = await api.translate({ text, target_lang: targetLanguage, domain }, token);
      setOutput(data.translation);
      setConfidence(data.confidence);
      setDetectedLanguage(data.source_lang ?? null);
      setTranslationId(data.id);
    } catch (err) {
      const description = err instanceof ApiError ? err.message : String(err);
      toast({ title: "Error", description });
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (rating: number) => {
    if (!token || !translationId || submittingFeedback) return;
    try {
      setSubmittingFeedback(true);
      await api.submitFeedback(translationId, { rating }, token);
      setFeedbackRating(rating);
      toast({ title: "Thanks for the feedback!" });
    } catch (err) {
      const description = err instanceof ApiError ? err.message : String(err);
      toast({ title: "Couldn't submit feedback", description });
    } finally {
      setSubmittingFeedback(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <Languages className="w-8 h-8 text-primary" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              Neural Translation
            </h1>
          </div>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Advanced AI-powered translation for low-resource languages with domain expertise and confidence scoring
          </p>
        </div>

        {/* Main Translation Interface */}
        <div className="max-w-6xl mx-auto">
          {/* Language Selection Bar */}
          <Card className="mb-6">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <Label className="text-sm font-medium mb-2 block">From</Label>
                  <Select value={sourceLanguage} onValueChange={setSourceLanguage}>
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {commonLanguages.map((lang) => (
                        <SelectItem key={lang.code} value={lang.code}>
                          <div className="flex items-center gap-2">
                            <span>{lang.flag}</span>
                            <span>{lang.name}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="mx-4 mt-6">
                  <Button 
                    variant="outline" 
                    size="icon"
                    onClick={swapLanguages}
                    disabled={sourceLanguage === "auto"}
                    className="rounded-full"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </Button>
                </div>

                <div className="flex-1">
                  <Label className="text-sm font-medium mb-2 block">To</Label>
                  <Select value={targetLanguage} onValueChange={setTargetLanguage}>
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {commonLanguages.filter(lang => lang.code !== "auto").map((lang) => (
                        <SelectItem key={lang.code} value={lang.code}>
                          <div className="flex items-center gap-2">
                            <span>{lang.flag}</span>
                            <span>{lang.name}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="ml-4 mt-6">
                  <Select value={domain} onValueChange={setDomain}>
                    <SelectTrigger className="w-48">
                      <SelectValue placeholder="Domain (Optional)" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="general">
                        <div className="flex items-center gap-2">
                          <Sparkles className="w-4 h-4" />
                          <span>General</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="medical">
                        <div className="flex items-center gap-2">
                          <span>🏥</span>
                          <span>Medical</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="legal">
                        <div className="flex items-center gap-2">
                          <span>⚖️</span>
                          <span>Legal</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="technical">
                        <div className="flex items-center gap-2">
                          <span>⚙️</span>
                          <span>Technical</span>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Translation Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Input Card */}
            <Card className="relative">
              <CardHeader className="flex flex-row items-center justify-between pb-3">
                <CardTitle className="text-lg font-semibold">Source Text</CardTitle>
                <div className="flex items-center gap-2">
                  {detectedLanguage && (
                    <Badge variant="secondary" className="text-xs">
                      Detected: {commonLanguages.find(l => l.code === detectedLanguage)?.name || detectedLanguage}
                    </Badge>
                  )}
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={clearAll}
                    disabled={!text && !output}
                  >
                    <RotateCcw className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Enter text to translate..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  className="min-h-[200px] resize-none text-base"
                />
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    {text.length} characters
                  </span>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(text)}
                      disabled={!text}
                    >
                      <Copy className="w-4 h-4 mr-1" />
                      Copy
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Output Card */}
            <Card className="relative">
              <CardHeader className="flex flex-row items-center justify-between pb-3">
                <CardTitle className="text-lg font-semibold">Translation</CardTitle>
                <div className="flex items-center gap-2">
                  {confidence !== null && (
                    <Badge 
                      variant={confidence > 0.8 ? "default" : confidence > 0.5 ? "secondary" : "destructive"}
                      className="text-xs"
                    >
                      <CheckCircle className="w-3 h-3 mr-1" />
                      {(confidence * 100).toFixed(0)}% confidence
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="min-h-[200px] rounded-md border bg-muted/10 p-4">
                  {loading ? (
                    <div className="flex items-center justify-center h-full">
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Clock className="w-4 h-4 animate-spin" />
                        <span>Translating...</span>
                      </div>
                    </div>
                  ) : output ? (
                    <p className="whitespace-pre-wrap text-base leading-relaxed">{output}</p>
                  ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground">
                      <div className="text-center">
                        <ArrowRight className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p>Translation will appear here</p>
                      </div>
                    </div>
                  )}
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    {output.length} characters
                  </span>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(output)}
                      disabled={!output}
                    >
                      <Copy className="w-4 h-4 mr-1" />
                      Copy
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!output}
                    >
                      <Volume2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                {output && translationId && (
                  <div className="flex items-center justify-between border-t pt-3">
                    <span className="text-sm text-muted-foreground">
                      {feedbackRating ? "Thanks for rating this translation" : "Was this translation accurate?"}
                    </span>
                    <div className="flex gap-2">
                      <Button
                        variant={feedbackRating === 5 ? "default" : "outline"}
                        size="sm"
                        onClick={() => submitFeedback(5)}
                        disabled={submittingFeedback || feedbackRating !== null}
                      >
                        <ThumbsUp className="w-4 h-4" />
                      </Button>
                      <Button
                        variant={feedbackRating === 1 ? "destructive" : "outline"}
                        size="sm"
                        onClick={() => submitFeedback(1)}
                        disabled={submittingFeedback || feedbackRating !== null}
                      >
                        <ThumbsDown className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Translate Button */}
          <div className="flex justify-center mt-8">
            <Button
              size="lg"
              onClick={runTranslate}
              disabled={loading || !text}
              className="px-12 py-6 text-lg font-semibold bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5 animate-spin" />
                  <span>Translating...</span>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Languages className="w-5 h-5" />
                  <span>Translate</span>
                </div>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Translate;
