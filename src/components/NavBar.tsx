import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Menu, Globe, Brain } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/context/AuthContext";

const NavBar = () => {
  const navigate = useNavigate();
  const { isAuthenticated, logout, user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const canReview = user?.role?.name === "translator" || user?.role?.name === "admin";

  const handleLogout = async () => {
    await logout();
    navigate("/login");
    setIsOpen(false);
  };

  const navigation = [
    { name: "Features", href: "/features" },
    { name: "Translate", href: "/translate" },
    { name: "API Docs", href: "/api-docs" },
    { name: "Pricing", href: "/pricing" },
    ...(isAuthenticated ? [{ name: "Analytics", href: "/analytics" }] : []),
    ...(canReview ? [{ name: "Review Queue", href: "/review" }] : []),
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex items-center justify-between py-4 px-4">
        {/* Logo */}
        <Link to="/" className="flex items-center space-x-2 font-semibold tracking-tight">
          <div className="flex items-center justify-center w-8 h-8 bg-primary rounded-lg">
            <Brain className="w-5 h-5 text-primary-foreground" />
          </div>
          <span className="text-lg">NMT Agent</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-8">
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              {item.name}
            </Link>
          ))}
        </nav>

        {/* Desktop Auth Buttons */}
        <div className="hidden md:flex items-center space-x-3">
          {isAuthenticated ? (
            <Button variant="outline" onClick={handleLogout}>
              Logout
            </Button>
          ) : (
            <>
              <Button variant="ghost" asChild>
                <Link to="/login">Sign In</Link>
              </Button>
              <Button asChild>
                <Link to="/login">Get Started</Link>
              </Button>
            </>
          )}
        </div>

        {/* Mobile Menu */}
        <Sheet open={isOpen} onOpenChange={setIsOpen}>
          <SheetTrigger asChild className="md:hidden">
            <Button variant="ghost" size="sm">
              <Menu className="w-5 h-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="right" className="w-[300px]">
            <div className="flex flex-col space-y-6 mt-6">
              <Link 
                to="/" 
                className="flex items-center space-x-2 font-semibold"
                onClick={() => setIsOpen(false)}
              >
                <div className="flex items-center justify-center w-8 h-8 bg-primary rounded-lg">
                  <Brain className="w-5 h-5 text-primary-foreground" />
                </div>
                <span className="text-lg">NMT Agent</span>
              </Link>
              
              <nav className="flex flex-col space-y-4">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="text-foreground hover:text-primary transition-colors"
                    onClick={() => setIsOpen(false)}
                  >
                    {item.name}
                  </Link>
                ))}
              </nav>

              <div className="flex flex-col space-y-3 pt-4 border-t">
                {isAuthenticated ? (
                  <Button variant="outline" onClick={handleLogout} className="w-full">
                    Logout
                  </Button>
                ) : (
                  <>
                    <Button 
                      variant="ghost" 
                      asChild 
                      className="w-full"
                      onClick={() => setIsOpen(false)}
                    >
                      <Link to="/login">Sign In</Link>
                    </Button>
                    <Button 
                      asChild 
                      className="w-full"
                      onClick={() => setIsOpen(false)}
                    >
                      <Link to="/login">Get Started</Link>
                    </Button>
                  </>
                )}
              </div>
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  );
};

export default NavBar;
