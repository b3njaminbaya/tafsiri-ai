import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { Cookie, Settings, X } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';

interface CookiePreferences {
  essential: boolean;
  analytics: boolean;
  functional: boolean;
  marketing: boolean;
}

const CookieConsent = () => {
  const { isAuthenticated } = useAuth();
  const [showBanner, setShowBanner] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [preferences, setPreferences] = useState<CookiePreferences>({
    essential: true,
    analytics: false,
    functional: false,
    marketing: false,
  });

  useEffect(() => {
    const consent = localStorage.getItem('cookie-consent');
    if (!consent) {
      setShowBanner(true);
    } else {
      const savedPreferences = JSON.parse(consent);
      setPreferences(savedPreferences);
    }
  }, []);

  // The account-level Privacy Dashboard has its own analytics/functional/
  // marketing switches backed by the same three concepts as this banner.
  // Without this, accepting/rejecting cookies here never touched those
  // account settings (and saving them there never touched this banner's
  // localStorage) — a signed-in user could "Reject All" here while their
  // account-level flags stayed on from before, with nothing reconciling the
  // two. Best-effort and non-blocking: this banner must keep working even
  // if the save fails or the user isn't logged in.
  const syncToAccountIfLoggedIn = (prefs: CookiePreferences) => {
    if (!isAuthenticated) return;
    api
      .updatePrivacySettings({
        analytics: prefs.analytics,
        functional: prefs.functional,
        marketing: prefs.marketing,
      })
      .catch(() => undefined);
  };

  const handleAcceptAll = () => {
    const allAccepted = {
      essential: true,
      analytics: true,
      functional: true,
      marketing: true,
    };
    setPreferences(allAccepted);
    localStorage.setItem('cookie-consent', JSON.stringify(allAccepted));
    syncToAccountIfLoggedIn(allAccepted);
    setShowBanner(false);
  };

  const handleRejectAll = () => {
    const essentialOnly = {
      essential: true,
      analytics: false,
      functional: false,
      marketing: false,
    };
    setPreferences(essentialOnly);
    localStorage.setItem('cookie-consent', JSON.stringify(essentialOnly));
    syncToAccountIfLoggedIn(essentialOnly);
    setShowBanner(false);
  };

  const handleCustomize = () => {
    setShowPreferences(true);
  };

  const handleSavePreferences = () => {
    localStorage.setItem('cookie-consent', JSON.stringify(preferences));
    syncToAccountIfLoggedIn(preferences);
    setShowBanner(false);
    setShowPreferences(false);
  };

  if (!showBanner) return null;

  return (
    <>
      {/* Cookie Banner */}
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-background border-t-2 border-t-brand/20 shadow-xl p-4">
        <div className="container flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3 flex-1">
            <Cookie className="h-5 w-5 text-brand mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <p className="font-medium mb-1">We use cookies to enhance your experience</p>
              <p className="text-muted-foreground">
                We use cookies to provide you with the best experience on our website. You can customize your preferences or accept all cookies.
              </p>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCustomize}
              className="flex items-center gap-2"
            >
              <Settings className="h-4 w-4" />
              Customize
            </Button>
            <Button variant="outline" size="sm" onClick={handleRejectAll}>
              Reject All
            </Button>
            <Button size="sm" onClick={handleAcceptAll}>
              Accept All
            </Button>
          </div>
        </div>
      </div>

      {/* Cookie Preferences Dialog */}
      <Dialog open={showPreferences} onOpenChange={setShowPreferences}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Cookie Preferences</DialogTitle>
            <DialogDescription>
              Manage your cookie preferences. Essential cookies are required for the website to function properly.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Essential Cookies */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">Essential Cookies</h3>
                  <p className="text-sm text-muted-foreground">
                    Required for the website to function properly
                  </p>
                </div>
                <Checkbox checked={true} disabled />
              </div>
              <p className="text-xs text-muted-foreground">
                These cookies are necessary for authentication, security, and basic website functionality.
              </p>
            </div>

            {/* Analytics Cookies */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">Analytics Cookies</h3>
                  <p className="text-sm text-muted-foreground">
                    Help us understand how visitors interact with our website
                  </p>
                </div>
                <Checkbox
                  checked={preferences.analytics}
                  onCheckedChange={(checked) =>
                    setPreferences(prev => ({ ...prev, analytics: checked as boolean }))
                  }
                />
              </div>
              <p className="text-xs text-muted-foreground">
                These cookies collect anonymous data about page views, user behavior, and performance metrics.
              </p>
            </div>

            {/* Functional Cookies */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">Functional Cookies</h3>
                  <p className="text-sm text-muted-foreground">
                    Enable enhanced functionality and personalization
                  </p>
                </div>
                <Checkbox
                  checked={preferences.functional}
                  onCheckedChange={(checked) =>
                    setPreferences(prev => ({ ...prev, functional: checked as boolean }))
                  }
                />
              </div>
              <p className="text-xs text-muted-foreground">
                These cookies remember your preferences like language settings and theme choices.
              </p>
            </div>

            {/* Marketing Cookies */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">Marketing Cookies</h3>
                  <p className="text-sm text-muted-foreground">
                    Used to deliver relevant advertisements
                  </p>
                </div>
                <Checkbox
                  checked={preferences.marketing}
                  onCheckedChange={(checked) =>
                    setPreferences(prev => ({ ...prev, marketing: checked as boolean }))
                  }
                />
              </div>
              <p className="text-xs text-muted-foreground">
                These cookies track your browsing habits to show you personalized ads and measure campaign effectiveness.
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPreferences(false)}>
              Cancel
            </Button>
            <Button onClick={handleSavePreferences}>
              Save Preferences
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default CookieConsent;