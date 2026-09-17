import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Search, Download, Globe, Loader2, Upload } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import {
  api,
  ApiError,
  type DatasetRecord,
  type RoadmapLanguage,
  type SupportedLanguage,
} from "@/lib/api";
import { toast } from "@/hooks/use-toast";

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KB", "MB", "GB"];
  let value = bytes / 1024;
  let unitIndex = 0;
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }
  return `${value.toFixed(1)} ${units[unitIndex]}`;
}

const Datasets = () => {
  const { isAuthenticated } = useAuth();
  const [datasets, setDatasets] = useState<DatasetRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [uploadOpen, setUploadOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    name: "",
    description: "",
    source_lang: "",
    target_lang: "",
    domain: "",
  });
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [supportedLanguages, setSupportedLanguages] = useState<SupportedLanguage[]>([]);
  const [roadmapLanguages, setRoadmapLanguages] = useState<RoadmapLanguage[]>([]);

  const loadDatasets = async () => {
    try {
      setLoading(true);
      const data = await api.listDatasets();
      setDatasets(data);
    } catch (err) {
      const description = err instanceof ApiError ? err.message : String(err);
      toast({ title: "Failed to load datasets", description });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDatasets();
    api.getLanguages().then((res) => setSupportedLanguages(res.languages)).catch(() => setSupportedLanguages([]));
    api
      .getLanguagesRoadmap()
      .then((res) => setRoadmapLanguages(res.languages))
      .catch(() => setRoadmapLanguages([]));
  }, []);

  // Datasets can be tagged with a roadmap language (one with no code isn't
  // selectable — those are cluster languages like Mijikenda without a single
  // standard code, see ml-service's KENYAN_LANGUAGES_ROADMAP) even though
  // translation isn't live for it yet — this is how data collection for a
  // not-yet-supported Kenyan language actually starts.
  const languageNameByCode = useMemo(() => {
    const map = new Map<string, string>();
    for (const lang of supportedLanguages) map.set(lang.code, lang.name);
    for (const lang of roadmapLanguages) if (lang.code) map.set(lang.code, lang.name);
    return map;
  }, [supportedLanguages, roadmapLanguages]);

  const filteredDatasets = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return datasets;
    return datasets.filter((d) =>
      [d.name, d.description, d.domain, d.source_lang, d.target_lang]
        .filter(Boolean)
        .some((field) => field!.toLowerCase().includes(query))
    );
  }, [datasets, search]);

  const handleDownload = async (id: number) => {
    if (!isAuthenticated) {
      toast({ title: "Log in to download datasets" });
      return;
    }
    try {
      const { url } = await api.getDatasetDownloadUrl(id);
      window.open(url, "_blank", "noopener,noreferrer");
    } catch (err) {
      const description = err instanceof ApiError ? err.message : String(err);
      toast({ title: "Download failed", description });
    }
  };

  const handleUpload = async () => {
    if (!isAuthenticated) return;
    if (!uploadForm.name || !uploadFile) {
      toast({ title: "Name and file are required" });
      return;
    }
    try {
      setUploading(true);
      await api.uploadDataset({ ...uploadForm, file: uploadFile });
      toast({ title: "Dataset uploaded" });
      setUploadOpen(false);
      setUploadForm({ name: "", description: "", source_lang: "", target_lang: "", domain: "" });
      setUploadFile(null);
      loadDatasets();
    } catch (err) {
      const description = err instanceof ApiError ? err.message : String(err);
      toast({ title: "Upload failed", description });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Kenyan Language Datasets
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Parallel corpora contributed by the community. Swahili and Somali already have real
          translation support — for every other Kenyan language on the roadmap, this is where
          that support starts: real translation needs real parallel text, and that has to come
          from people who actually speak these languages.
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              placeholder="Search datasets by name, language, or domain..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-24 text-muted-foreground">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          Loading datasets...
        </div>
      ) : filteredDatasets.length === 0 ? (
        <div className="text-center py-24 text-muted-foreground">
          {datasets.length === 0
            ? "No datasets have been uploaded yet — be the first to contribute one below."
            : "No datasets match your search."}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {filteredDatasets.map((dataset) => (
            <Card key={dataset.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <Globe className="h-5 w-5 text-primary" />
                    {dataset.domain && <Badge variant="outline">{dataset.domain}</Badge>}
                  </div>
                </div>
                <CardTitle className="text-lg">{dataset.name}</CardTitle>
                {dataset.description && (
                  <CardDescription>{dataset.description}</CardDescription>
                )}
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Languages:</span>
                    <br />
                    <span className="font-medium">
                      {dataset.source_lang && dataset.target_lang
                        ? `${languageNameByCode.get(dataset.source_lang) ?? dataset.source_lang} → ${
                            languageNameByCode.get(dataset.target_lang) ?? dataset.target_lang
                          }`
                        : "Unspecified"}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Size:</span>
                    <br />
                    <span className="font-medium">{formatSize(dataset.size_bytes)}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between pt-2">
                  <span className="text-sm text-muted-foreground">
                    {new Date(dataset.created_at).toLocaleDateString()}
                  </span>
                  <Button
                    size="sm"
                    onClick={() => handleDownload(dataset.id)}
                    title={isAuthenticated ? undefined : "Log in to download datasets"}
                  >
                    <Download className="h-4 w-4" />
                    {isAuthenticated ? "Download" : "Log in to download"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <div className="bg-muted rounded-lg p-8 text-center">
        <h2 className="text-2xl font-bold mb-4">Contribute a Dataset</h2>
        <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
          Have parallel text for Kikuyu, Luo, Kalenjin, or another Kenyan language — even a small
          amount? Upload it here. This is the data a future fine-tuning effort for that language
          would actually be built from.
        </p>
        {isAuthenticated ? (
          <Dialog open={uploadOpen} onOpenChange={setUploadOpen}>
            <DialogTrigger asChild>
              <Button size="lg">
                <Upload className="h-4 w-4 mr-1" />
                Upload Dataset
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>Upload a dataset</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="ds-name">Name *</Label>
                  <Input
                    id="ds-name"
                    value={uploadForm.name}
                    onChange={(e) => setUploadForm((p) => ({ ...p, name: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="ds-description">Description</Label>
                  <Textarea
                    id="ds-description"
                    value={uploadForm.description}
                    onChange={(e) => setUploadForm((p) => ({ ...p, description: e.target.value }))}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="ds-source">Source language</Label>
                    <Select
                      value={uploadForm.source_lang}
                      onValueChange={(value) => setUploadForm((p) => ({ ...p, source_lang: value }))}
                    >
                      <SelectTrigger id="ds-source">
                        <SelectValue placeholder="Select..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectLabel>Supported</SelectLabel>
                          {supportedLanguages.map((lang) => (
                            <SelectItem key={lang.code} value={lang.code}>
                              {lang.name}
                            </SelectItem>
                          ))}
                        </SelectGroup>
                        <SelectGroup>
                          <SelectLabel>Kenyan — data collection only</SelectLabel>
                          {roadmapLanguages
                            .filter((lang) => lang.code)
                            .map((lang) => (
                              <SelectItem key={lang.code} value={lang.code as string}>
                                {lang.name}
                              </SelectItem>
                            ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="ds-target">Target language</Label>
                    <Select
                      value={uploadForm.target_lang}
                      onValueChange={(value) => setUploadForm((p) => ({ ...p, target_lang: value }))}
                    >
                      <SelectTrigger id="ds-target">
                        <SelectValue placeholder="Select..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectLabel>Supported</SelectLabel>
                          {supportedLanguages.map((lang) => (
                            <SelectItem key={lang.code} value={lang.code}>
                              {lang.name}
                            </SelectItem>
                          ))}
                        </SelectGroup>
                        <SelectGroup>
                          <SelectLabel>Kenyan — data collection only</SelectLabel>
                          {roadmapLanguages
                            .filter((lang) => lang.code)
                            .map((lang) => (
                              <SelectItem key={lang.code} value={lang.code as string}>
                                {lang.name}
                              </SelectItem>
                            ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  Contributing a parallel corpus for a language marked "data collection only" is
                  exactly how that language moves toward real translation support — see the{" "}
                  <Link to="/translate" className="underline">
                    Translate page
                  </Link>{" "}
                  for the current roadmap.
                </p>
                <div className="space-y-2">
                  <Label htmlFor="ds-domain">Domain</Label>
                  <Input
                    id="ds-domain"
                    placeholder="medical, legal, general..."
                    value={uploadForm.domain}
                    onChange={(e) => setUploadForm((p) => ({ ...p, domain: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="ds-file">File *</Label>
                  <Input
                    id="ds-file"
                    type="file"
                    accept=".tsv,.csv,.txt,.json,.jsonl,.tmx,.xliff,.xlf"
                    onChange={(e) => setUploadFile(e.target.files?.[0] ?? null)}
                  />
                  <p className="text-xs text-muted-foreground">
                    Accepted formats: TSV, CSV, TXT, JSON, JSONL, TMX, XLIFF
                  </p>
                </div>
              </div>
              <DialogFooter>
                <Button onClick={handleUpload} disabled={uploading}>
                  {uploading ? "Uploading..." : "Upload"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        ) : (
          <Button size="lg" asChild>
            <Link to="/login">Log in to upload</Link>
          </Button>
        )}
      </div>
    </div>
  );
};

export default Datasets;
