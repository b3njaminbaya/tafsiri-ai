import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
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
import { api, ApiError, type DatasetRecord } from "@/lib/api";
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
  const { token, isAuthenticated } = useAuth();
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
  }, []);

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
    try {
      const { url } = await api.getDatasetDownloadUrl(id);
      window.open(url, "_blank", "noopener,noreferrer");
    } catch (err) {
      const description = err instanceof ApiError ? err.message : String(err);
      toast({ title: "Download failed", description });
    }
  };

  const handleUpload = async () => {
    if (!token) return;
    if (!uploadForm.name || !uploadFile) {
      toast({ title: "Name and file are required" });
      return;
    }
    try {
      setUploading(true);
      await api.uploadDataset({ ...uploadForm, file: uploadFile }, token);
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
          Translation Datasets
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Parallel corpora contributed by the community — uploaded and stored for training and evaluating translation models.
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
                        ? `${dataset.source_lang} → ${dataset.target_lang}`
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
                  <Button size="sm" onClick={() => handleDownload(dataset.id)}>
                    <Download className="h-4 w-4" />
                    Download
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <div className="bg-muted rounded-lg p-8 text-center">
        <h2 className="text-2xl font-bold mb-4">Upload Your Own Dataset</h2>
        <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
          Contribute to the community by sharing your parallel corpora. Help improve translation quality for everyone.
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
                    <Input
                      id="ds-source"
                      placeholder="en"
                      value={uploadForm.source_lang}
                      onChange={(e) => setUploadForm((p) => ({ ...p, source_lang: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="ds-target">Target language</Label>
                    <Input
                      id="ds-target"
                      placeholder="sw"
                      value={uploadForm.target_lang}
                      onChange={(e) => setUploadForm((p) => ({ ...p, target_lang: e.target.value }))}
                    />
                  </div>
                </div>
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
                    onChange={(e) => setUploadFile(e.target.files?.[0] ?? null)}
                  />
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
