import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Link } from "react-router-dom";
import { Shield, Lock, Users, KeyRound, ShieldCheck, GitPullRequest, CheckCircle } from "lucide-react";

const Security = () => {
  const securityFeatures = [
    {
      icon: <Lock className="h-6 w-6" />,
      title: "Encryption in Transit",
      description: "Traffic between your browser and the API is served over HTTPS/TLS.",
    },
    {
      icon: <KeyRound className="h-6 w-6" />,
      title: "Password & API Key Hashing",
      description: "Passwords are hashed with bcrypt; API keys are hashed at rest (SHA-256) and shown to you only once, at creation.",
    },
    {
      icon: <ShieldCheck className="h-6 w-6" />,
      title: "httpOnly Session Cookies",
      description: "The web app authenticates via an httpOnly cookie, which JavaScript cannot read — a stolen script can't exfiltrate your session token.",
    },
    {
      icon: <Users className="h-6 w-6" />,
      title: "Role-Based Access Control",
      description: "User, translator, and admin roles gate what each account can see and do, enforced on every request server-side.",
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Rate Limiting",
      description: "Authentication and translation endpoints are rate-limited per caller to reduce abuse.",
    },
    {
      icon: <GitPullRequest className="h-6 w-6" />,
      title: "Open About Gaps",
      description: "This page describes what's actually implemented today, not aspirational claims — see the note below.",
    },
  ];

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">Security</h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          An honest account of the security measures actually built into Tafsiri AI today.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
        {securityFeatures.map((feature, index) => (
          <Card key={index}>
            <CardHeader>
              <div className="text-primary mb-2">{feature.icon}</div>
              <CardTitle className="text-lg">{feature.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>{feature.description}</CardDescription>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="max-w-3xl mx-auto space-y-6 mb-16">
        <div>
          <h2 className="text-2xl font-bold mb-4">Who can see your translations</h2>
          <p className="text-muted-foreground">
            Your translations are not end-to-end encrypted, and we do not claim a zero-knowledge
            architecture. Translations you submit are stored so you can access your own history,
            and low-confidence translations enter an active-learning review queue where accounts
            with the translator or admin role can read them in order to submit corrections that
            improve future translation quality. Admins can also manage user accounts and platform
            content. There is no reviewer access to your account's authentication credentials
            (passwords are hashed, API keys are hashed) — only to the translation content itself,
            and only for the review workflow described here.
          </p>
        </div>

        <div>
          <h2 className="text-2xl font-bold mb-4">What we don't claim</h2>
          <p className="text-muted-foreground">
            Tafsiri AI does not currently hold SOC 2, ISO 27001, or HIPAA certifications, does not
            run a dedicated 24/7 security team, and does not operate a bug bounty program. If any
            of these matter for your use case, please{" "}
            <Link to="/contact" className="text-primary underline">
              get in touch
            </Link>{" "}
            before relying on this platform for that requirement.
          </p>
        </div>

        <div>
          <h2 className="text-2xl font-bold mb-4">Data rights</h2>
          <p className="text-muted-foreground">
            You can export everything your account touches, and delete your account (anonymizing
            your personal data while preserving referential content like translations and dataset
            uploads other parts of the platform depend on) from the{" "}
            <Link to="/privacy-settings" className="text-primary underline">
              Privacy Dashboard
            </Link>
            . See the{" "}
            <Link to="/privacy-policy" className="text-primary underline">
              Privacy Policy
            </Link>{" "}
            for the full picture.
          </p>
        </div>
      </div>

      <div className="text-center">
        <h2 className="text-3xl font-bold mb-4">Found a security issue?</h2>
        <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
          If you discover a security vulnerability, please let us know via the contact form rather
          than filing a public issue.
        </p>
        <div className="flex items-center justify-center gap-2">
          <CheckCircle className="h-4 w-4 text-primary" />
          <Link to="/contact" className="text-primary underline font-medium">
            Report it here
          </Link>
        </div>
        <div className="mt-2">
          <Badge variant="outline">No bug bounty program at this time</Badge>
        </div>
      </div>
    </div>
  );
};

export default Security;
