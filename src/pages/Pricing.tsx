import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, Star } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { api, ApiError, type Plan } from "@/lib/api";

const marketingPlans = [
  {
    name: "Free",
    price: "$0",
    period: "/month",
    description: "Perfect for testing and small projects",
    features: [
      "Full language coverage, including low-resource African languages",
      "Standard API rate limits",
      "Community forum support",
    ],
  },
  {
    name: "Pro",
    price: "Varies",
    period: "",
    description: "Higher API quota for businesses and developers",
    features: [
      "Higher API usage quota (see plans below)",
      "Full language coverage",
      "Domain-specific glossary terminology forcing",
      "Translation analytics dashboard",
    ],
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For large-scale deployments",
    features: [
      "Custom API quota",
      "Full language coverage",
      "Priority support",
      "Talk to us about your specific needs",
    ],
  },
];

const Pricing = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loadingPlans, setLoadingPlans] = useState(true);
  const [checkingOut, setCheckingOut] = useState<string | null>(null);
  const plansSectionRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    api
      .getPlans()
      .then(setPlans)
      .catch(() => setPlans([]))
      .finally(() => setLoadingPlans(false));
  }, []);

  const subscribe = async (priceId: string) => {
    if (!isAuthenticated) {
      toast({ title: "Please log in to subscribe" });
      navigate("/login");
      return;
    }
    setCheckingOut(priceId);
    try {
      const { checkout_url } = await api.createCheckoutSession(priceId);
      window.location.href = checkout_url;
    } catch (error) {
      toast({
        title: "Couldn't start checkout",
        description: error instanceof ApiError ? error.message : String(error),
        variant: "destructive",
      });
    } finally {
      setCheckingOut(null);
    }
  };

  const billingConfigured = plans.length > 0;

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Simple, Transparent Pricing
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Choose the perfect plan for your translation needs. All plans include our core features with no hidden fees.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
        {marketingPlans.map((plan) => (
          <Card key={plan.name} className={`relative ${plan.popular ? 'border-primary shadow-lg scale-105' : ''}`}>
            {plan.popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <Badge className="flex items-center gap-1">
                  <Star className="h-3 w-3" />
                  Most Popular
                </Badge>
              </div>
            )}
            <CardHeader className="text-center pb-8">
              <CardTitle className="text-2xl">{plan.name}</CardTitle>
              <div className="mt-4">
                <span className="text-4xl font-bold">{plan.price}</span>
                <span className="text-muted-foreground">{plan.period}</span>
              </div>
              <CardDescription className="mt-2">{plan.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <ul className="space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary flex-shrink-0" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
              {plan.name === "Free" ? (
                <Button className="w-full" variant="outline" asChild>
                  <Link to={isAuthenticated ? "/translate" : "/login"}>Get Started</Link>
                </Button>
              ) : plan.name === "Enterprise" ? (
                <Button className="w-full" variant="outline" asChild>
                  <Link to="/contact">Contact Sales</Link>
                </Button>
              ) : (
                <div className="space-y-1">
                  <Button
                    className="w-full"
                    variant="default"
                    disabled={!billingConfigured || loadingPlans}
                    onClick={() => {
                      if (!billingConfigured) return;
                      // There's no stable mapping between this fixed marketing
                      // tier and an arbitrary admin-configured Stripe price —
                      // if there's exactly one real plan it's unambiguous, but
                      // with more than one, guessing (e.g. always plans[0])
                      // could subscribe someone to a plan other than the one
                      // shown here. Send them to the real, named list instead.
                      if (plans.length === 1) {
                        subscribe(plans[0].price_id);
                      } else {
                        plansSectionRef.current?.scrollIntoView({ behavior: "smooth" });
                      }
                    }}
                  >
                    {loadingPlans
                      ? "Loading..."
                      : !billingConfigured
                        ? "Coming soon"
                        : plans.length === 1
                          ? checkingOut === plans[0]?.price_id
                            ? "Redirecting..."
                            : "Subscribe"
                          : "View plans"}
                  </Button>
                  {!loadingPlans && !billingConfigured && (
                    <p className="text-xs text-muted-foreground text-center">
                      Subscriptions aren't enabled on this deployment yet.
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {billingConfigured && plans.length > 1 && (
        <div ref={plansSectionRef} className="max-w-4xl mx-auto mb-16 scroll-mt-24">
          <h2 className="text-2xl font-bold text-center mb-6">Available Subscription Plans</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {plans.map((plan) => (
              <Card key={plan.price_id}>
                <CardContent className="pt-6 flex items-center justify-between gap-4">
                  <div>
                    <p className="font-medium">{plan.price_id}</p>
                    <p className="text-sm text-muted-foreground">
                      {plan.quota_limit.toLocaleString()} requests/month
                    </p>
                  </div>
                  <Button
                    onClick={() => subscribe(plan.price_id)}
                    disabled={checkingOut === plan.price_id}
                  >
                    {checkingOut === plan.price_id ? "Redirecting..." : "Subscribe"}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      <div className="text-center mt-16 space-y-4">
        <h3 className="text-2xl font-semibold">Need a custom solution?</h3>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          We offer custom enterprise solutions with dedicated infrastructure, specialized models, and tailored support.
        </p>
        <Button size="lg" asChild>
          <Link to="/contact">Contact Sales Team</Link>
        </Button>
      </div>
    </div>
  );
};

export default Pricing;
