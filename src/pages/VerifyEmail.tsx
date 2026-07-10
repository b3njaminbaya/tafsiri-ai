import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";
import { api, ApiError } from "@/lib/api";

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setError("This link is missing its verification token.");
      return;
    }
    api
      .verifyEmail(token)
      .then(() => setStatus("success"))
      .catch((err) => {
        setStatus("error");
        setError(err instanceof ApiError ? err.message : String(err));
      });
  }, [token]);

  return (
    <div className="min-h-[calc(100vh-140px)] bg-background flex items-center justify-center">
      <div className="container mx-auto max-w-md py-12 text-center">
        {status === "loading" && (
          <>
            <Loader2 className="h-10 w-10 mx-auto mb-4 animate-spin text-muted-foreground" />
            <h1 className="text-2xl font-bold mb-2">Verifying your email...</h1>
          </>
        )}
        {status === "success" && (
          <>
            <CheckCircle2 className="h-10 w-10 mx-auto mb-4 text-primary" />
            <h1 className="text-2xl font-bold mb-2">Email verified</h1>
            <p className="text-muted-foreground mb-6">Your email address has been confirmed.</p>
            <Link to="/translate" className="underline">
              Continue to the app
            </Link>
          </>
        )}
        {status === "error" && (
          <>
            <XCircle className="h-10 w-10 mx-auto mb-4 text-destructive" />
            <h1 className="text-2xl font-bold mb-2">Verification failed</h1>
            <p className="text-muted-foreground mb-6">{error || "This link is invalid or has expired."}</p>
            <Link to="/login" className="underline">
              Back to log in
            </Link>
          </>
        )}
      </div>
    </div>
  );
};

export default VerifyEmail;
