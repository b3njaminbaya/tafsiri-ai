import { useState } from "react";
import PageContainer from "@/components/layout/PageContainer";
import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Mail, MessageSquare, Users, Headphones, Loader2 } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const SUBJECT_OPTIONS: Record<string, string> = {
  general: "General Inquiry",
  technical: "Technical Support",
  billing: "Billing Question",
  partnership: "Partnership",
  feedback: "Product Feedback",
};

const contactMethods = [
  {
    icon: <Mail className="h-6 w-6" />,
    title: "Email",
    description: "Send a message using the form below",
    contact: "Use the contact form",
    response: "Within a few business days",
  },
  {
    icon: <MessageSquare className="h-6 w-6" />,
    title: "Community Forum",
    description: "Ask questions and get help from other users",
    contact: "/community",
    response: "Varies",
  },
  {
    icon: <Users className="h-6 w-6" />,
    title: "API Documentation",
    description: "Answers to most technical and integration questions",
    contact: "/api-docs",
    response: "Self-service",
  },
];

const Contact = () => {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim() || !form.subject || !form.message.trim()) {
      toast({ title: "Please fill in all fields" });
      return;
    }
    try {
      setSubmitting(true);
      await api.submitContactMessage({
        name: form.name.trim(),
        email: form.email.trim(),
        subject: SUBJECT_OPTIONS[form.subject] ?? form.subject,
        message: form.message.trim(),
      });
      toast({ title: "Message sent", description: "We'll get back to you soon." });
      setForm({ name: "", email: "", subject: "", message: "" });
    } catch (err) {
      const description = err instanceof ApiError ? err.message : String(err);
      toast({ title: "Failed to send message", description });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <PageContainer>
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">Contact Us</h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Get in touch with any questions about the Tafsiri AI platform.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
        <div>
          <h2 className="text-2xl font-bold mb-6">Send us a message</h2>
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                placeholder="Enter your name"
                value={form.name}
                onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email address"
                value={form.email}
                onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="subject">Subject</Label>
              <Select
                value={form.subject}
                onValueChange={(value) => setForm((p) => ({ ...p, subject: value }))}
              >
                <SelectTrigger id="subject">
                  <SelectValue placeholder="Select a topic" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(SUBJECT_OPTIONS).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="message">Message</Label>
              <Textarea
                id="message"
                placeholder="Tell us how we can help you..."
                className="min-h-32"
                value={form.message}
                onChange={(e) => setForm((p) => ({ ...p, message: e.target.value }))}
                required
              />
            </div>

            <Button type="submit" size="lg" className="w-full" disabled={submitting}>
              {submitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" /> Sending...
                </>
              ) : (
                "Send Message"
              )}
            </Button>
          </form>
        </div>

        <div className="space-y-8">
          <div>
            <h2 className="text-2xl font-bold mb-6">Get in touch</h2>
            <div className="grid grid-cols-1 gap-4">
              {contactMethods.map((method, index) => (
                <Card key={index}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3">
                      <div className="text-primary">{method.icon}</div>
                      <CardTitle className="text-lg">{method.title}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="mb-2">{method.description}</CardDescription>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">{method.contact}</span>
                      <span className="text-muted-foreground">{method.response}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-muted rounded-lg p-8 text-center">
        <Headphones className="h-12 w-12 mx-auto mb-4 text-primary" />
        <h3 className="text-2xl font-semibold mb-2">Need immediate help?</h3>
        <p className="text-muted-foreground mb-4">
          Check the documentation and community forum for quick answers to common questions.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button variant="outline" asChild>
            <Link to="/api-docs">View Documentation</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/community">Visit Community Forum</Link>
          </Button>
        </div>
      </div>
    </PageContainer>
  );
};

export default Contact;
