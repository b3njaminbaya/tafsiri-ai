import { useMemo, useState } from "react";
import PageContainer from "@/components/layout/PageContainer";
import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Book, Search, ArrowRight, Clock, Users, Mail } from "lucide-react";

const FAQS = [
  {
    question: "How do I get started with the Tafsiri AI API?",
    answer: "Create an account, then generate an API key from your account (email verification required for API access). Check the API Docs page for endpoint reference and code examples, and use the interactive docs at /docs on the backend to try requests directly.",
  },
  {
    question: "What languages are supported for translation?",
    answer: "Tafsiri AI is Kenya-first: Swahili and Somali are fully supported today. Other Kenyan languages (Kikuyu, Luo, Kalenjin, Kamba, Kisii, Maasai, Luhya, and more) are on the roadmap — see the Translate page for the current list of what's supported versus planned. A number of other African and world languages are also available; see the API Docs page for the current full list.",
  },
  {
    question: "How is pricing calculated?",
    answer: "Available plans and their API quotas are listed on the Pricing page and are fetched live from the account you sign up with — pricing isn't fixed content, so check that page for current tiers.",
  },
  {
    question: "Can I train custom models?",
    answer: "Not yet. Domain-specific terminology (medical, legal, technical) is supported via a constrained-decoding glossary that forces the correct term into translations, but there is no self-service custom model training pipeline at this time.",
  },
  {
    question: "What are the API rate limits?",
    answer: "Single translations are limited to 60 requests/minute per caller, and batch translation (up to 50 texts per call) to 20 requests/minute. API keys also have an independent usage quota tied to your plan.",
  },
  {
    question: "Is my data secure?",
    answer: "Translations are transmitted over HTTPS and access to your account data is protected by authentication and role-based access control. Translator/admin reviewers can see translations flagged for the active-learning review queue as part of the product's quality-improvement workflow. See the Security and Privacy Policy pages for details.",
  },
  {
    question: "How accurate are the translations?",
    answer: "Every translation includes a confidence score derived from the model's own output. Low-confidence translations are automatically queued for human review and correction, which is the core mechanism this product uses to improve quality over time — there's no independently audited BLEU score to quote yet.",
  },
  {
    question: "Do you offer support for real-time applications?",
    answer: "The API is a standard synchronous REST API; there is currently no WebSocket or streaming interface.",
  },
];

const Support = () => {
  const [searchQuery, setSearchQuery] = useState("");

  const supportOptions = [
    {
      icon: <Book className="h-8 w-8" />,
      title: "Documentation",
      description: "Comprehensive guides and API references",
      availability: "Always available",
      response: "Self-service",
      button: "Browse Docs",
      to: "/api-docs",
    },
    {
      icon: <Mail className="h-8 w-8" />,
      title: "Contact Support",
      description: "Send us a message and we'll get back to you",
      availability: "Anytime",
      response: "Within a few business days",
      button: "Send a Message",
      to: "/contact",
    },
  ];

  const filteredFaqs = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return FAQS;
    return FAQS.filter(
      (faq) =>
        faq.question.toLowerCase().includes(query) || faq.answer.toLowerCase().includes(query)
    );
  }, [searchQuery]);

  const resources = [
    {
      title: "API Documentation",
      description: "Complete API reference with code examples",
      link: "/api-docs",
      icon: <Book className="h-5 w-5" />,
    },
    {
      title: "Community Forum",
      description: "Connect with other users and get help",
      link: "/community",
      icon: <Users className="h-5 w-5" />,
    },
    {
      title: "Status Page",
      description: "Live status of the API, database, cache, and translation model",
      link: "/status",
      icon: <Clock className="h-5 w-5" />,
    },
  ];

  const quickLinks = [
    "Account Setup",
    "API Authentication",
    "Rate Limits",
    "Billing Questions",
    "Domain Terminology",
    "Data Privacy",
  ];

  return (
    <PageContainer>
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">Support Center</h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Find answers, get help, and learn how to make the most of the Tafsiri AI platform.
        </p>
      </div>

      <div className="mb-12">
        <div className="relative max-w-2xl mx-auto">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground h-5 w-5" />
          <Input
            placeholder="Search FAQs..."
            className="pl-12 h-14 text-lg"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16 max-w-3xl mx-auto">
        {supportOptions.map((option, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardHeader className="text-center">
              <div className="mx-auto text-primary mb-4">{option.icon}</div>
              <CardTitle className="text-lg">{option.title}</CardTitle>
              <CardDescription>{option.description}</CardDescription>
            </CardHeader>
            <CardContent className="text-center space-y-3">
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Available:</span>
                  <span className="font-medium">{option.availability}</span>
                </div>
                <div className="flex justify-between">
                  <span>Response:</span>
                  <span className="font-medium">{option.response}</span>
                </div>
              </div>
              <Button className="w-full" asChild>
                <Link to={option.to}>{option.button}</Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <div id="faq" className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
        <div className="lg:col-span-2">
          <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions</h2>
          {filteredFaqs.length === 0 ? (
            <p className="text-muted-foreground">
              No FAQs match "{searchQuery}".{" "}
              <Link to="/contact" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
                Contact us
              </Link>{" "}
              with your question instead.
            </p>
          ) : (
            <Accordion type="single" collapsible className="space-y-4">
              {filteredFaqs.map((faq, index) => (
                <AccordionItem key={index} value={`item-${index}`}>
                  <AccordionTrigger className="text-left hover:no-underline">
                    {faq.question}
                  </AccordionTrigger>
                  <AccordionContent className="text-muted-foreground leading-relaxed">
                    {faq.answer}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Links</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {quickLinks.map((link, index) => (
                  <button
                    key={index}
                    onClick={() => setSearchQuery(link)}
                    className="w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-muted rounded-md transition-colors"
                  >
                    <span>{link}</span>
                    <ArrowRight className="h-4 w-4" />
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Need More Help?</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="mb-4">
                Can't find what you're looking for? Send us a message.
              </CardDescription>
              <Button variant="outline" className="w-full" asChild>
                <Link to="/contact">Contact Support</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold mb-6 text-center">Helpful Resources</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {resources.map((resource, index) => (
            <Link key={index} to={resource.link}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-3">
                    <div className="text-primary">{resource.icon}</div>
                    <CardTitle className="text-base">{resource.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="mb-3">{resource.description}</CardDescription>
                  <div className="flex items-center text-primary text-sm font-medium">
                    <span>Learn more</span>
                    <ArrowRight className="h-4 w-4 ml-1" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </PageContainer>
  );
};

export default Support;
