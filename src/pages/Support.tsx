import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { MessageSquare, Book, Video, FileText, Search, ArrowRight, Clock, Users } from "lucide-react";

const Support = () => {
  const supportOptions = [
    {
      icon: <MessageSquare className="h-8 w-8" />,
      title: "Live Chat",
      description: "Get instant help from our support team",
      availability: "9 AM - 6 PM PST",
      response: "< 5 minutes",
      button: "Start Chat"
    },
    {
      icon: <Book className="h-8 w-8" />,
      title: "Documentation",
      description: "Comprehensive guides and API references",
      availability: "Always available",
      response: "Self-service",
      button: "Browse Docs"
    },
    {
      icon: <Video className="h-8 w-8" />,
      title: "Video Tutorials",
      description: "Step-by-step video guides and webinars",
      availability: "On-demand",
      response: "Immediate",
      button: "Watch Videos"
    },
    {
      icon: <FileText className="h-8 w-8" />,
      title: "Submit Ticket",
      description: "Detailed support for complex issues",
      availability: "24/7",
      response: "< 24 hours",
      button: "Create Ticket"
    }
  ];

  const faqs = [
    {
      question: "How do I get started with the Tafsiri AI API?",
      answer: "Getting started is easy! First, create an account and generate your API key from the dashboard. Then, check our Quick Start guide in the documentation for code examples in multiple programming languages. You can also use our interactive API explorer to test endpoints before implementing them in your application."
    },
    {
      question: "What languages are supported for translation?",
      answer: "We currently support over 100 languages with high-quality translation models. Popular language pairs include English, Spanish, French, German, Chinese, Japanese, Korean, Arabic, Russian, and many more. Check our language support page for the complete list and quality ratings for each language pair."
    },
    {
      question: "How is pricing calculated?",
      answer: "Pricing is based on the number of characters translated. We offer flexible pricing tiers: Free (1K characters/month), Pro ($49/month for 500K characters), and Enterprise (custom pricing for unlimited usage). Usage beyond your plan limit is charged at competitive per-character rates."
    },
    {
      question: "Can I train custom models?",
      answer: "Yes! Pro and Enterprise plans include custom model training capabilities. You can upload your own parallel datasets to train specialized models for your domain (legal, medical, technical, etc.). Custom models typically show 15-30% improvement in accuracy for domain-specific content."
    },
    {
      question: "What are the API rate limits?",
      answer: "Rate limits vary by plan: Free (10 requests/minute), Pro (100 requests/minute), Enterprise (custom limits). If you need higher limits, contact our sales team. We also offer burst capacity for occasional traffic spikes."
    },
    {
      question: "Is my data secure?",
      answer: "Absolutely. We use end-to-end encryption (TLS 1.3), store data in SOC 2 compliant data centers, and are GDPR compliant. Translation requests are processed securely and not used to train our models without explicit consent. Enterprise customers can opt for dedicated instances and data residency controls."
    },
    {
      question: "How accurate are the translations?",
      answer: "Our neural machine translation models achieve industry-leading BLEU scores: 35-45+ for major language pairs. Accuracy varies by language pair and domain. Custom models trained on your data can achieve even higher accuracy. We provide confidence scores with each translation to help you assess quality."
    },
    {
      question: "Do you offer support for real-time applications?",
      answer: "Yes, our API is optimized for real-time use with typical response times under 200ms for standard requests. We offer WebSocket connections for streaming applications and have global CDN endpoints to minimize latency worldwide."
    }
  ];

  const resources = [
    {
      title: "API Documentation",
      description: "Complete API reference with code examples",
      link: "/api-docs",
      icon: <Book className="h-5 w-5" />
    },
    {
      title: "SDK Downloads",
      description: "Official SDKs for Python, JavaScript, and more",
      link: "/downloads",
      icon: <FileText className="h-5 w-5" />
    },
    {
      title: "Community Forum",
      description: "Connect with other developers and get help",
      link: "/community",
      icon: <Users className="h-5 w-5" />
    },
    {
      title: "Status Page",
      description: "Real-time service status and uptime monitoring",
      link: "/status",
      icon: <Clock className="h-5 w-5" />
    }
  ];

  const quickLinks = [
    "Account Setup",
    "API Authentication",
    "Error Codes",
    "Billing Questions",
    "Model Training",
    "Enterprise Features",
    "Webhook Configuration",
    "Data Privacy"
  ];

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">Support Center</h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Find answers, get help, and learn how to make the most of our neural machine translation platform.
        </p>
      </div>

      <div className="mb-12">
        <div className="relative max-w-2xl mx-auto">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground h-5 w-5" />
          <Input 
            placeholder="Search for help articles, guides, and FAQs..."
            className="pl-12 pr-12 h-14 text-lg"
          />
          <Button className="absolute right-2 top-2 h-10">Search</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
        {supportOptions.map((option, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardHeader className="text-center">
              <div className="mx-auto text-primary mb-4">
                {option.icon}
              </div>
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
              <Button className="w-full">{option.button}</Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
        <div className="lg:col-span-2">
          <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions</h2>
          <Accordion type="single" collapsible className="space-y-4">
            {faqs.map((faq, index) => (
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
              <CardTitle className="text-lg">Support Hours</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Live Chat:</span>
                <span>9 AM - 6 PM PST</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Email:</span>
                <span>24/7</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Phone (Enterprise):</span>
                <span>24/7</span>
              </div>
              <div className="pt-3 border-t">
                <Badge variant="outline" className="w-full justify-center">
                  All times in Pacific Standard Time
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Need More Help?</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="mb-4">
                Can't find what you're looking for? Our team is here to help.
              </CardDescription>
              <div className="space-y-2">
                <Button variant="outline" className="w-full">
                  Contact Support
                </Button>
                <Button variant="outline" className="w-full">
                  Schedule a Call
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold mb-6 text-center">Helpful Resources</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {resources.map((resource, index) => (
            <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer">
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
          ))}
        </div>
      </div>
    </div>
  );
};

export default Support;