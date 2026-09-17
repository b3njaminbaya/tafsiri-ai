import { Link, useLocation } from "react-router-dom";
import { useEffect } from "react";
import PageContainer from "@/components/layout/PageContainer";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-[calc(100vh-140px)] flex items-center justify-center bg-background">
      <PageContainer className="py-0 text-center">
        <h1 className="text-4xl font-bold mb-4">404</h1>
        <p className="text-xl text-muted-foreground mb-4">Oops! Page not found</p>
        <Link to="/" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
          Return to Home
        </Link>
      </PageContainer>
    </div>
  );
};

export default NotFound;
