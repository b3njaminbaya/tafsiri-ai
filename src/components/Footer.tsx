import { Link } from "react-router-dom";
import { Separator } from "@/components/ui/separator";
import { Github, Twitter, Linkedin, Mail } from "lucide-react";

const Footer = () => {
  return (
    <footer className="dark bg-background border-t">
      <div className="container py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg">Tafsiri AI</h3>
            <p className="text-sm text-muted-foreground">
              Neural machine translation for Kenya's languages, starting with Swahili and Somali.
            </p>
            <div className="flex space-x-3">
              <a 
                href="https://twitter.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-brand transition-colors"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-brand transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
              <a 
                href="https://linkedin.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-brand transition-colors"
              >
                <Linkedin className="w-5 h-5" />
              </a>
              <a 
                href="mailto:contact@tafsiri.ai"
                className="text-muted-foreground hover:text-brand transition-colors"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Product */}
          <div className="space-y-4">
            <h4 className="font-semibold">Product</h4>
            <div className="space-y-2">
              <Link to="/translate" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                Translator
              </Link>
              <Link to="/features" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                Features
              </Link>
              <Link to="/api-docs" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                API Documentation
              </Link>
              <Link to="/pricing" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                Pricing
              </Link>
              <Link to="/datasets" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                Datasets
              </Link>
            </div>
          </div>

          {/* Resources */}
          <div className="space-y-4">
            <h4 className="font-semibold">Resources</h4>
            <div className="space-y-2">
              <Link to="/blog" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                Blog
              </Link>
              <Link to="/support" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                Support
              </Link>
              <Link to="/community" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                Community Forum
              </Link>
              <Link to="/status" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                System Status
              </Link>
            </div>
          </div>

          {/* Legal */}
          <div className="space-y-4">
            <h4 className="font-semibold">Legal</h4>
            <div className="space-y-2">
              <Link to="/privacy-policy" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                Privacy Policy
              </Link>
              <Link to="/terms-of-service" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                Terms of Service
              </Link>
              <Link to="/cookie-policy" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                Cookie Policy
              </Link>
              <Link to="/gdpr-compliance" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                GDPR Compliance
              </Link>
              <Link to="/security" className="block text-sm text-muted-foreground hover:text-brand transition-colors">
                Security
              </Link>
            </div>
          </div>
        </div>

        <Separator className="my-8" />
        
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="text-sm text-muted-foreground">
            © 2026 Tafsiri AI. All rights reserved.
          </div>
          <div className="flex flex-wrap items-center gap-6 text-sm text-muted-foreground">
            <span>Built for underserved communities</span>
            <Link to="/accessibility" className="hover:text-brand transition-colors">
              Accessibility
            </Link>
            <Link to="/contact" className="hover:text-brand transition-colors">
              Contact
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;