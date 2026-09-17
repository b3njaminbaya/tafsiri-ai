import { Link } from "react-router-dom";
import PageContainer from "@/components/layout/PageContainer";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bot, Globe, Shield, Database, Users, BarChart3, Code } from "lucide-react";

const Features = () => {
  const features = [
    {
      icon: <Bot className="h-8 w-8" />,
      title: "Neural Machine Translation",
      description: "Meta's M2M100 multilingual model, many-to-many translation with no English pivot required.",
      badge: "AI-Powered"
    },
    {
      icon: <Globe className="h-8 w-8" />,
      title: "Kenya-First Language Coverage",
      description: "Swahili and Somali are fully supported today; Kikuyu, Luo, Kalenjin, Kamba, Kisii, Maasai, and more Kenyan languages are on the roadmap.",
      badge: "Kenya"
    },
    {
      icon: <Shield className="h-8 w-8" />,
      title: "Real Account Security",
      description: "bcrypt password hashing, hashed API keys, httpOnly session cookies, and role-based access control — see the Security page for exactly what's implemented.",
      badge: "Secure"
    },
    {
      icon: <Database className="h-8 w-8" />,
      title: "Domain Terminology",
      description: "Medical, legal, and technical glossaries that force the correct term into translations via constrained decoding — admin-managed, not fixed.",
      badge: "Customizable"
    },
    {
      icon: <Users className="h-8 w-8" />,
      title: "Community & Review Queue",
      description: "A real discussion forum, dataset sharing, and an active-learning review queue where translators correct low-confidence translations.",
      badge: "Collaborative"
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "Translation Analytics",
      description: "Personal and (for admins) platform-wide dashboards covering translation volume, confidence, and language pairs.",
      badge: "Analytics"
    },
    {
      icon: <Code className="h-8 w-8" />,
      title: "Developer API",
      description: "A REST API authenticated via X-API-Key, with rate limiting and per-key usage quotas — see the API Docs page for endpoints and examples.",
      badge: "Developer"
    }
  ];

  return (
    <PageContainer>
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Built for Kenya's Languages
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          What Tafsiri AI actually does today, starting with Swahili and Somali.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {features.map((feature, index) => (
          <Card key={index} className="relative overflow-hidden">
            <CardHeader>
              <div className="flex items-center justify-between mb-2">
                <div className="text-primary">
                  {feature.icon}
                </div>
                <Badge variant="secondary">{feature.badge}</Badge>
              </div>
              <CardTitle className="text-lg">{feature.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-sm leading-relaxed">
                {feature.description}
              </CardDescription>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-20 text-center">
        <h2 className="text-3xl font-bold mb-4">Not there yet</h2>
        <p className="text-muted-foreground max-w-2xl mx-auto mb-6">
          We don't claim SOC 2/ISO 27001 certification, a guaranteed uptime SLA, or custom model
          training — see the{" "}
          <Link to="/security" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
            Security page
          </Link>{" "}
          for the honest picture, and the{" "}
          <Link to="/translate" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
            Translate page
          </Link>{" "}
          for the full Kenyan-language roadmap.
        </p>
      </div>
    </PageContainer>
  );
};

export default Features;