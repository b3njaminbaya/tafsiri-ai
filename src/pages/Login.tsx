import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "@/hooks/use-toast";
import { useAuth } from "@/context/AuthContext";

const Login = () => {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register } = useAuth();

  const redirectTo = (location.state as { from?: { pathname: string } })?.from?.pathname ?? "/translate";

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
          <div className="flex items-center justify-between mt-4 text-sm">
            <span className="text-muted-foreground">{mode === "login" ? "New here?" : "Already have an account?"}</span>
            <Button variant="link" onClick={() => setMode(mode === "login" ? "signup" : "login")}>{mode === "login" ? "Create one" : "Log in"}</Button>
          </div>
          <div className="mt-6">
            <p className="text-sm mb-2">Social login</p>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={() => toast({ title: "Coming soon", description: "Google OAuth will be added next." })}>Google</Button>
              <Button variant="secondary" onClick={() => toast({ title: "Coming soon", description: "GitHub OAuth will be added next." })}>GitHub</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
