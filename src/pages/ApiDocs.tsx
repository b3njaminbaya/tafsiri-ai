import { Link } from "react-router-dom";
import PageContainer from "@/components/layout/PageContainer";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Code, Copy, Play } from "lucide-react";
import { API_BASE } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

// API_BASE already includes the /api/v1 prefix; the interactive Swagger UI
// FastAPI generates for free lives at the backend root's /docs, not under
// /api/v1 — this is a real, working "try it" console, unlike a fictional
// in-house API explorer.
const BACKEND_ROOT = API_BASE.replace(/\/api\/v1\/?$/, "");
const SWAGGER_URL = `${BACKEND_ROOT}/docs`;

const ApiDocs = () => {
  const copyCode = async (code: string) => {
    try {
      await navigator.clipboard.writeText(code);
      toast({ title: "Copied to clipboard" });
    } catch {
      toast({ title: "Could not copy — select and copy manually" });
    }
  };

  const endpoints = [
    {
      method: "POST",
      path: "/api/v1/translate/",
      description: "Translate a single piece of text",
      badge: "Core"
    },
    {
      method: "POST",
      path: "/api/v1/translate/batch",
      description: "Translate up to 50 texts in one call — real batched inference where possible",
      badge: "Batch"
    },
    {
      method: "GET",
      path: "/api/v1/translate/history",
      description: "List your own past translations",
      badge: "Core"
    },
    {
      method: "POST",
      path: "/api/v1/translate/{id}/feedback",
      description: "Rate one of your own past translations",
      badge: "Core"
    },
    {
      method: "GET",
      path: "/api/v1/languages",
      description: "Get supported languages",
      badge: "Info"
    },
    {
      method: "GET",
      path: "/api/v1/models",
      description: "The translation model currently serving requests",
      badge: "Models"
    }
  ];

  const codeExamples = {
    curl: `curl -X POST ${API_BASE}/translate/ \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Hello, world!",
    "source_lang": "en",
    "target_lang": "es"
  }'`,
    javascript: `const response = await fetch('${API_BASE}/translate/', {
  method: 'POST',
  headers: {
    'X-API-Key': 'YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'Hello, world!',
    source_lang: 'en',
    target_lang: 'es'
  })
});

const data = await response.json();
console.log(data.translation);`,
    python: `import requests

response = requests.post(
    '${API_BASE}/translate/',
    headers={
        'X-API-Key': 'YOUR_API_KEY',
        'Content-Type': 'application/json'
    },
    json={
        'text': 'Hello, world!',
        'source_lang': 'en',
        'target_lang': 'es'
    }
)

data = response.json()
print(data['translation'])`
  };

  return (
    <PageContainer>
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">API Documentation</h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Integrate Kenya-first neural machine translation — Swahili and Somali today — into your applications with our RESTful API.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
        <div>
          <h2 className="text-2xl font-bold mb-6">API Endpoints</h2>
          <div className="space-y-4">
            {endpoints.map((endpoint, index) => (
              <Card key={index}>
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Badge variant={endpoint.method === "POST" ? "default" : "secondary"}>
                        {endpoint.method}
                      </Badge>
                      <code className="text-sm font-mono">{endpoint.path}</code>
                    </div>
                    <Badge variant="outline">{endpoint.badge}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{endpoint.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-bold mb-6">Getting Started</h2>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5" />
                Quick Start
              </CardTitle>
              <CardDescription>
                Get your API key and start translating in minutes
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <h4 className="font-semibold">1. Get your API key</h4>
                <p className="text-sm text-muted-foreground">
                  Sign up, verify your email, then generate a key from the{" "}
                  <Link to="/privacy-settings" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
                    API Keys tab
                  </Link>{" "}
                  of your account.
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">2. Make your first request</h4>
                <p className="text-sm text-muted-foreground">Use the examples below to integrate with your application</p>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">3. Handle responses</h4>
                <p className="text-sm text-muted-foreground">Process the JSON response containing your translation</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold mb-6">Code Examples</h2>
        <Tabs defaultValue="curl" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="curl">cURL</TabsTrigger>
            <TabsTrigger value="javascript">JavaScript</TabsTrigger>
            <TabsTrigger value="python">Python</TabsTrigger>
          </TabsList>
          {Object.entries(codeExamples).map(([lang, code]) => (
            <TabsContent key={lang} value={lang}>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="text-lg capitalize">{lang} Example</CardTitle>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => copyCode(code)}>
                      <Copy className="h-4 w-4" />
                      Copy
                    </Button>
                    <Button variant="outline" size="sm" asChild>
                      <a href={SWAGGER_URL} target="_blank" rel="noopener noreferrer">
                        <Play className="h-4 w-4" />
                        Try it
                      </a>
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-4 rounded-md overflow-x-auto">
                    <code className="text-sm">{code}</code>
                  </pre>
                </CardContent>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </PageContainer>
  );
};

export default ApiDocs;