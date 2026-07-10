import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, ApiError } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.forgotPassword(email);
      setSent(true);
    } catch (err) {
      const description = err instanceof ApiError ? err.message : String(err);
      toast({ title: "Error", description });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-140px)] bg-background flex items-center justify-center">
      <div className="container mx-auto max-w-md py-12">
        <h1 className="text-3xl font-bold mb-2">Reset your password</h1>
        <p className="text-muted-foreground mb-6">
          Enter your email and we'll send you a link to reset your password.
        </p>
        <div className="rounded-lg border p-6">
          {sent ? (
            <p className="text-sm">
              If that email is registered, a reset link has been sent. Check your inbox (or, in
              local development without SMTP configured, check the backend server logs for the
              link).
            </p>
          ) : (
            <form onSubmit={onSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? "Sending..." : "Send reset link"}
              </Button>
            </form>
          )}
          <div className="mt-4 text-sm text-center">
            <Link to="/login" className="text-muted-foreground hover:text-foreground underline">
              Back to log in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
