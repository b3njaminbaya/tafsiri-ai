import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bot, Globe, Zap, Shield, Database, Users, BarChart3, Code } from "lucide-react";

const Features = () => {
  const features = [
    {
      icon: <Bot className="h-8 w-8" />,
      title: "Neural Machine Translation",
      description: "State-of-the-art NMT models powered by transformer architecture for accurate translations across 100+ languages.",
      badge: "AI-Powered"
    },
    {
      icon: <Globe className="h-8 w-8" />,
      title: "100+ Languages",
      description: "Support for major world languages with continuous expansion of language pairs and specialized domains.",
      badge: "Global"
    },
    {
      icon: <Zap className="h-8 w-8" />,
      title: "Real-time Translation",
      description: "Lightning-fast translation API with sub-second response times and 99.9% uptime guarantee.",
      badge: "Fast"
    },
    {
      icon: <Shield className="h-8 w-8" />,
      title: "Enterprise Security",
      description: "SOC 2 compliant with end-to-end encryption, GDPR compliance, and enterprise-grade data protection.",
      badge: "Secure"
    },
    {
      icon: <Database className="h-8 w-8" />,
      title: "Custom Models",
      description: "Train specialized models on your domain-specific data for improved accuracy in technical translations.",
      badge: "Customizable"
    },
    {
      icon: <Users className="h-8 w-8" />,
      title: "Team Collaboration",
      description: "Built-in collaboration tools with translation memories, glossaries, and quality assurance workflows.",
      badge: "Collaborative"
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "Advanced Analytics",
      description: "Detailed insights into translation quality, usage patterns, and performance metrics for optimization.",
      badge: "Analytics"
    },
    {
      icon: <Code className="h-8 w-8" />,
      title: "Developer-Friendly API",
      description: "RESTful API with SDKs for popular programming languages and comprehensive documentation.",
      badge: "Developer"
    }
  ];

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Powerful Features for Modern Translation
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Discover the comprehensive suite of features that make Tafsiri AI the choice of enterprises worldwide.
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
        <h2 className="text-3xl font-bold mb-8">Enterprise-Ready Platform</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">99.9% Uptime</h3>
            <p className="text-muted-foreground">Guaranteed availability with global infrastructure</p>
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">Sub-second Response</h3>
            <p className="text-muted-foreground">Lightning-fast translation processing</p>
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">SOC 2 Compliant</h3>
            <p className="text-muted-foreground">Enterprise-grade security and compliance</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Features;