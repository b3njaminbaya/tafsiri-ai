import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, ApiError } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      toast({ title: "Missing reset token", description: "Use the link from your reset email." });
      return;
    }
    setSubmitting(true);
    try {
      await api.resetPassword(token, password);
      toast({ title: "Password updated", description: "You can now log in with your new password." });
      navigate("/login", { replace: true });
    } catch (err) {
      const description = err instanceof ApiError ? err.message : String(err);
      toast({ title: "Couldn't reset password", description });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-140px)] bg-background flex items-center justify-center">
      <div className="container mx-auto max-w-md py-12">
        <h1 className="text-3xl font-bold mb-2">Set a new password</h1>
        <p className="text-muted-foreground mb-6">Choose a new password for your account.</p>
        <div className="rounded-lg border p-6">
          {!token ? (
            <p className="text-sm text-destructive">
              This link is missing its reset token. Request a new one from the{" "}
              <Link to="/forgot-password" className="underline">
                forgot password
              </Link>{" "}
              page.
            </p>
          ) : (
            <form onSubmit={onSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="password">New password</Label>
                <Input
                  id="password"
                  type="password"
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? "Updating..." : "Update password"}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;
