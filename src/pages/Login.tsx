import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "@/hooks/use-toast";
import { useAuth } from "@/context/AuthContext";
import { api, API_BASE } from "@/lib/api";

const OAUTH_ERROR_MESSAGES: Record<string, string> = {
  invalid_state: "That login link expired or was tampered with. Please try again.",
  failed: "We couldn't complete sign-in with that provider. Please try again.",
};

const Login = () => {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [oauthProviders, setOauthProviders] = useState<{ google: boolean; github: boolean } | null>(
    null
  );
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { login, register } = useAuth();

  const redirectTo = (location.state as { from?: { pathname: string } })?.from?.pathname ?? "/translate";

  useEffect(() => {
    api
      .getOAuthProviders()
      .then(setOauthProviders)
      .catch(() => setOauthProviders({ google: false, github: false }));
  }, []);

  useEffect(() => {
    const oauthError = searchParams.get("oauth_error");
    if (oauthError) {
      toast({
        title: "Sign-in failed",
        description: OAUTH_ERROR_MESSAGES[oauthError] ?? "Something went wrong signing you in.",
      });
    }
  }, [searchParams]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (mode === "signup") {
        await register(email, password);
        toast({ title: "Account created", description: "You can now log in." });
        setMode("login");
        return;
      }
      await login(email, password);
      toast({ title: "Welcome", description: "Logged in successfully." });
      navigate(redirectTo, { replace: true });
    } catch (err) {
      toast({ title: "Error", description: String(err) });
    } finally {
      setSubmitting(false);
    }
  };

  const startOAuth = (provider: "google" | "github") => {
    window.location.href = `${API_BASE}/auth/oauth/${provider}/login`;
  };

  return (
    <div className="min-h-[calc(100vh-140px)] bg-background flex items-center justify-center">
      <div className="container mx-auto max-w-md py-12">
        <h1 className="text-3xl font-bold mb-2">{mode === "login" ? "Log in" : "Create an account"}</h1>
        <p className="text-muted-foreground mb-6">Access the NMT Agent platform.</p>
        <div className="rounded-lg border p-6">
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? "Please wait..." : mode === "login" ? "Log in" : "Sign up"}
            </Button>
          </form>
          {mode === "login" && (
            <div className="mt-3 text-right text-sm">
              <Link to="/forgot-password" className="text-muted-foreground hover:text-foreground underline">
                Forgot password?
              </Link>
            </div>
          )}
          <div className="flex items-center justify-between mt-4 text-sm">
            <span className="text-muted-foreground">{mode === "login" ? "New here?" : "Already have an account?"}</span>
            <Button variant="link" onClick={() => setMode(mode === "login" ? "signup" : "login")}>{mode === "login" ? "Create one" : "Log in"}</Button>
          </div>
          <div className="mt-6">
            <p className="text-sm mb-2">Social login</p>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                disabled={!oauthProviders?.google}
                title={oauthProviders && !oauthProviders.google ? "Google sign-in isn't configured on this server" : undefined}
                onClick={() => startOAuth("google")}
              >
                {oauthProviders?.google === false ? "Google (not configured)" : "Google"}
              </Button>
              <Button
                variant="secondary"
                disabled={!oauthProviders?.github}
                title={oauthProviders && !oauthProviders.github ? "GitHub sign-in isn't configured on this server" : undefined}
                onClick={() => startOAuth("github")}
              >
                {oauthProviders?.github === false ? "GitHub (not configured)" : "GitHub"}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
