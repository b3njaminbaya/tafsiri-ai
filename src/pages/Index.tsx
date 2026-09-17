import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Link } from "react-router-dom";
import {
  Globe,
  Brain,
  Users,
  BarChart3,
  Shield,
  Zap,
  CheckCircle,
  Star,
  ArrowRight,
  Languages,
  Database,
  Cpu
} from "lucide-react";
import { api, type CommunityStats } from "@/lib/api";

const Index = () => {
  const [stats, setStats] = useState<CommunityStats | null>(null);

  useEffect(() => {
    api.getCommunityStats().then(setStats).catch(() => setStats(null));
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative bg-background pt-20 pb-16 md:pt-32 md:pb-24">
        <div className="container">
          <div className="text-center max-w-4xl mx-auto">
            <Badge className="mb-6" variant="secondary">
              <Star className="w-4 h-4 mr-2" />
              Kenya-First Neural Machine Translation
            </Badge>
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 text-foreground">
              Tafsiri AI
            </h1>
            <p className="text-xl md:text-2xl text-foreground max-w-3xl mx-auto mb-8 leading-relaxed">
              Neural machine translation for Kenya's languages — Swahili and Somali today, with
              Kikuyu, Luo, Kalenjin, and more on the roadmap — backed by an active-learning review
              queue that improves quality over time.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Button size="lg" className="text-lg px-8 py-6 ring-2 ring-brand/40 hover:ring-brand/70 transition-shadow" asChild>
                <Link to="/translate">
                  Start Translating <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 py-6" asChild>
                <Link to="/login">Get Started Free</Link>
              </Button>
            </div>

            {/* Stats — real platform activity, not marketing placeholders */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto">
              <div className="text-center">
                <div className="text-2xl md:text-3xl font-bold text-primary">2 / 68</div>
                <div className="text-sm text-muted-foreground">Kenyan languages supported so far</div>
              </div>
              <div className="text-center">
                <div className="text-2xl md:text-3xl font-bold text-primary">
                  {stats ? stats.total_translations.toLocaleString() : "—"}
                </div>
                <div className="text-sm text-muted-foreground">Translations served</div>
              </div>
              <div className="text-center">
                <div className="text-2xl md:text-3xl font-bold text-primary">
                  {stats ? stats.total_contributors.toLocaleString() : "—"}
                </div>
                <div className="text-sm text-muted-foreground">Contributors</div>
              </div>
              <div className="text-center">
                <div className="text-2xl md:text-3xl font-bold text-primary">
                  {stats ? stats.total_datasets.toLocaleString() : "—"}
                </div>
                <div className="text-sm text-muted-foreground">Datasets shared</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 md:py-24">
        <div className="container">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Cutting-Edge Translation Technology</h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Our advanced AI platform combines the latest in machine learning to deliver unprecedented 
              translation quality for low-resource languages.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <Brain className="w-12 h-12 text-primary mb-4" />
                <CardTitle>Transfer Learning</CardTitle>
                <CardDescription>
                  Leverage pre-trained multilingual models for instant language support
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Meta's M2M100 multilingual base model
                  </li>
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Many-to-many translation, no English pivot required
                  </li>
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Automatic source language detection
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <Zap className="w-12 h-12 text-primary mb-4" />
                <CardTitle>Domain Terminology</CardTitle>
                <CardDescription>
                  Force the correct domain-specific term into translations, without a training pipeline
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Medical, legal, and technical glossaries
                  </li>
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Constrained decoding guarantees the term appears
                  </li>
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Admin-managed terminology
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <Users className="w-12 h-12 text-primary mb-4" />
                <CardTitle>Active Learning</CardTitle>
                <CardDescription>
                  Continuous improvement through user feedback
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    User feedback integration
                  </li>
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Confidence scoring
                  </li>
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Human review queue for low-confidence results
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <Database className="w-12 h-12 text-primary mb-4" />
                <CardTitle>Dataset Management</CardTitle>
                <CardDescription>
                  Comprehensive tools for corpus management and versioning
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Format validation on upload
                  </li>
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Time-limited secure download links
                  </li>
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Community uploads
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <BarChart3 className="w-12 h-12 text-primary mb-4" />
                <CardTitle>Analytics Dashboard</CardTitle>
                <CardDescription>
                  Real-time insights into translation performance and usage
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Performance metrics
                  </li>
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Usage analytics
                  </li>
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Quality tracking
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <Shield className="w-12 h-12 text-primary mb-4" />
                <CardTitle>Enterprise Security</CardTitle>
                <CardDescription>
                  Bank-grade security with comprehensive access controls
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    OAuth2 + JWT
                  </li>
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Role-based access
                  </li>
                  <li className="flex items-center text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    API rate limiting
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-16 md:py-24 bg-secondary/5">
        <div className="container">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Perfect for Every Use Case</h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              From humanitarian aid to business expansion, our platform serves diverse translation needs
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <Globe className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Humanitarian Organizations</h3>
              <p className="text-muted-foreground">
                Enable communication in crisis zones and underserved communities with reliable translation services.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <Languages className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Government Agencies</h3>
              <p className="text-muted-foreground">
                Provide public services in multiple languages and support citizen engagement across linguistic barriers.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <Cpu className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Tech Companies</h3>
              <p className="text-muted-foreground">
                Integrate high-quality translation APIs into your applications and reach global markets.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-24">
        <div className="container">
          <div className="text-center max-w-3xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Ready to Break Language Barriers?
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Join thousands of organizations using our platform to connect communities worldwide.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="text-lg px-8 py-6" asChild>
                <Link to="/translate">
                  Try Free Translation <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 py-6" asChild>
                <Link to="/login">Create Account</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
