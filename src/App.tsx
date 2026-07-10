import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import NavBar from "@/components/NavBar";
import Footer from "@/components/Footer";
import CookieConsent from "@/components/CookieConsent";
import ProtectedRoute from "@/components/ProtectedRoute";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import Translate from "./pages/Translate";
import Features from "./pages/Features";
import ApiDocs from "./pages/ApiDocs";
import Pricing from "./pages/Pricing";
import Datasets from "./pages/Datasets";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import TermsOfService from "./pages/TermsOfService";
import CookiePolicy from "./pages/CookiePolicy";
import GdprCompliance from "./pages/GdprCompliance";
import Security from "./pages/Security";
import Contact from "./pages/Contact";
import Accessibility from "./pages/Accessibility";
import Community from "./pages/Community";
import SystemStatus from "./pages/SystemStatus";
import Blog from "./pages/Blog";
import Support from "./pages/Support";
import GdprRequest from "./pages/GdprRequest";
import PrivacySettings from "./pages/PrivacySettings";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <div className="flex flex-col min-h-screen">
            <NavBar />
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/login" element={<Login />} />
                <Route
                  path="/translate"
                  element={
                    <ProtectedRoute>
                      <Translate />
                    </ProtectedRoute>
                  }
                />
                <Route path="/features" element={<Features />} />
                <Route path="/api-docs" element={<ApiDocs />} />
                <Route path="/pricing" element={<Pricing />} />
                <Route path="/datasets" element={<Datasets />} />
                <Route path="/privacy-policy" element={<PrivacyPolicy />} />
                <Route path="/terms-of-service" element={<TermsOfService />} />
                <Route path="/cookie-policy" element={<CookiePolicy />} />
                <Route path="/gdpr-compliance" element={<GdprCompliance />} />
                <Route path="/security" element={<Security />} />
                <Route path="/contact" element={<Contact />} />
                <Route path="/accessibility" element={<Accessibility />} />
                <Route path="/community" element={<Community />} />
                <Route path="/status" element={<SystemStatus />} />
                <Route path="/blog" element={<Blog />} />
                <Route path="/support" element={<Support />} />
                <Route path="/gdpr-request" element={<GdprRequest />} />
                <Route path="/privacy-settings" element={<PrivacySettings />} />
                {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </main>
            <Footer />
          </div>
          <CookieConsent />
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
