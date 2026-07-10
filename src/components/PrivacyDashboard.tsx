import { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Shield,
  Cookie,
  Bell,
  Download,
  Trash2,
  Eye,
  Settings,
  Calendar,
  MapPin,
  Globe,
  Loader2,
  User as UserIcon,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/context/AuthContext';
import { api, ApiError, type PrivacySettings } from '@/lib/api';

const PrivacyDashboard = () => {
  const { toast } = useToast();
  const { user, logout, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [settings, setSettings] = useState<PrivacySettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [displayName, setDisplayName] = useState('');
  const [savingProfile, setSavingProfile] = useState(false);

  useEffect(() => {
    setDisplayName(user?.display_name ?? '');
  }, [user]);

  const handleSaveProfile = async () => {
    setSavingProfile(true);
    try {
      await api.updateProfile({ display_name: displayName.trim() || null });
      await refreshUser();
      toast({ title: 'Profile updated' });
    } catch (error) {
      toast({
        title: 'Couldn’t update profile',
        description: error instanceof ApiError ? error.message : String(error),
        variant: 'destructive',
      });
    } finally {
      setSavingProfile(false);
    }
  };

  useEffect(() => {
    api
      .getPrivacySettings()
      .then(setSettings)
      .catch((err) => {
        const description = err instanceof ApiError ? err.message : String(err);
        toast({ title: 'Failed to load privacy settings', description, variant: 'destructive' });
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSettingChange = async (key: keyof PrivacySettings, value: boolean) => {
    if (!settings) return;
    const previous = settings;
    setSettings({ ...settings, [key]: value });
    setSaving(key);
    try {
      const updated = await api.updatePrivacySettings({ [key]: value });
      setSettings(updated);
    } catch (error) {
      setSettings(previous);
      toast({
        title: 'Couldn’t save that setting',
        description: error instanceof ApiError ? error.message : String(error),
        variant: 'destructive',
      });
    } finally {
      setSaving(null);
    }
  };

  const handleDataExport = async () => {
    setExporting(true);
    try {
      const data = await api.exportMyData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `nmt-agent-data-export-${new Date().toISOString().slice(0, 10)}.json`;
      link.click();
      URL.revokeObjectURL(url);
      toast({
        title: 'Export ready',
        description: 'Your data has been downloaded as a JSON file.',
      });
    } catch (error) {
      toast({
        title: 'Export failed',
        description: error instanceof ApiError ? error.message : String(error),
        variant: 'destructive',
      });
    } finally {
      setExporting(false);
    }
  };

  const handleDataDeletion = async () => {
    if (
      !window.confirm(
        'Are you sure you want to delete your account? Your email and password will be permanently removed and your account deactivated. This cannot be undone.'
      )
    ) {
      return;
    }

    setDeleting(true);
    try {
      await api.deleteAccount();
      toast({
        title: 'Account deleted',
        description: 'Your account has been anonymized and deactivated.',
      });
      await logout();
      navigate('/');
    } catch (error) {
      toast({
        title: 'Deletion failed',
        description: error instanceof ApiError ? error.message : String(error),
        variant: 'destructive',
      });
    } finally {
      setDeleting(false);
    }
  };

  if (loading || !settings) {
    return (
      <div className="max-w-4xl mx-auto flex items-center justify-center py-24 text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin mr-2" />
        Loading your privacy settings...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Shield className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold">Privacy Dashboard</h1>
          <p className="text-muted-foreground">
            Manage your privacy settings and data preferences
          </p>
        </div>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <UserIcon className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="privacy" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Privacy
          </TabsTrigger>
          <TabsTrigger value="cookies" className="flex items-center gap-2">
            <Cookie className="h-4 w-4" />
            Cookies
          </TabsTrigger>
          <TabsTrigger value="communications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Communications
          </TabsTrigger>
          <TabsTrigger value="data" className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Data Rights
          </TabsTrigger>
        </TabsList>

        {/* Profile */}
        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserIcon className="h-5 w-5" />
                Public Display Name
              </CardTitle>
              <CardDescription>
                Shown on community leaderboards instead of your email address. Leave blank to
                fall back to the part of your email before the @.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2 max-w-sm">
                <Label htmlFor="display-name">Display name</Label>
                <Input
                  id="display-name"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  maxLength={50}
                  placeholder="e.g. Amina K."
                />
              </div>
              <Button onClick={handleSaveProfile} disabled={savingProfile}>
                {savingProfile ? 'Saving...' : 'Save profile'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Privacy Settings */}
        <TabsContent value="privacy" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Data Collection Preferences
              </CardTitle>
              <CardDescription>
                Control how we collect and use your personal data
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Globe className="h-4 w-4" />
                    <span className="font-medium">Analytics Data Collection</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Allow collection of usage analytics to improve our services
                  </p>
                </div>
                <Switch
                  checked={settings.data_collection}
                  disabled={saving === 'data_collection'}
                  onCheckedChange={(checked) => handleSettingChange('data_collection', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    <span className="font-medium">Location Tracking</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Allow location-based features and regional optimization
                  </p>
                </div>
                <Switch
                  checked={settings.location_tracking}
                  disabled={saving === 'location_tracking'}
                  onCheckedChange={(checked) => handleSettingChange('location_tracking', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    <span className="font-medium">Third-Party Data Sharing</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Allow sharing anonymized data with trusted partners
                  </p>
                </div>
                <Switch
                  checked={settings.third_party_sharing}
                  disabled={saving === 'third_party_sharing'}
                  onCheckedChange={(checked) => handleSettingChange('third_party_sharing', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Cookie Settings */}
        <TabsContent value="cookies" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cookie className="h-5 w-5" />
                Cookie Preferences
              </CardTitle>
              <CardDescription>
                Manage your cookie preferences for different types of cookies
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">Essential Cookies</span>
                    <Badge variant="secondary">Required</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Necessary for website functionality and security
                  </p>
                </div>
                <Switch checked disabled />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <span className="font-medium">Analytics Cookies</span>
                  <p className="text-sm text-muted-foreground">
                    Help us understand how visitors interact with our website
                  </p>
                </div>
                <Switch
                  checked={settings.analytics}
                  disabled={saving === 'analytics'}
                  onCheckedChange={(checked) => handleSettingChange('analytics', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <span className="font-medium">Functional Cookies</span>
                  <p className="text-sm text-muted-foreground">
                    Enable enhanced functionality and personalization
                  </p>
                </div>
                <Switch
                  checked={settings.functional}
                  disabled={saving === 'functional'}
                  onCheckedChange={(checked) => handleSettingChange('functional', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <span className="font-medium">Marketing Cookies</span>
                  <p className="text-sm text-muted-foreground">
                    Used to deliver relevant advertisements
                  </p>
                </div>
                <Switch
                  checked={settings.marketing}
                  disabled={saving === 'marketing'}
                  onCheckedChange={(checked) => handleSettingChange('marketing', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Communication Settings */}
        <TabsContent value="communications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Communication Preferences
              </CardTitle>
              <CardDescription>
                Control how we communicate with you
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <span className="font-medium">Email Marketing</span>
                  <p className="text-sm text-muted-foreground">
                    Receive promotional emails and newsletters
                  </p>
                </div>
                <Switch
                  checked={settings.email_marketing}
                  disabled={saving === 'email_marketing'}
                  onCheckedChange={(checked) => handleSettingChange('email_marketing', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <span className="font-medium">SMS Marketing</span>
                  <p className="text-sm text-muted-foreground">
                    Receive promotional text messages
                  </p>
                </div>
                <Switch
                  checked={settings.sms_marketing}
                  disabled={saving === 'sms_marketing'}
                  onCheckedChange={(checked) => handleSettingChange('sms_marketing', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Bell className="h-4 w-4" />
                    <span className="font-medium">Push Notifications</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Receive browser notifications for important updates
                  </p>
                </div>
                <Switch
                  checked={settings.push_notifications}
                  disabled={saving === 'push_notifications'}
                  onCheckedChange={(checked) => handleSettingChange('push_notifications', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Data Rights */}
        <TabsContent value="data" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Your Data Rights
              </CardTitle>
              <CardDescription>
                Exercise your rights under GDPR and other privacy regulations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {user && (
                <Alert>
                  <Calendar className="h-4 w-4" />
                  <AlertDescription>
                    Account created: {new Date(user.created_at).toLocaleDateString()}
                  </AlertDescription>
                </Alert>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Button
                  variant="outline"
                  className="flex items-center gap-2"
                  onClick={handleDataExport}
                  disabled={exporting}
                >
                  <Download className="h-4 w-4" />
                  {exporting ? 'Preparing export...' : 'Export My Data'}
                </Button>

                <Button
                  variant="outline"
                  className="flex items-center gap-2"
                  onClick={handleDataDeletion}
                  disabled={deleting}
                >
                  <Trash2 className="h-4 w-4" />
                  {deleting ? 'Deleting...' : 'Delete My Account'}
                </Button>
              </div>

              <div className="text-sm text-muted-foreground space-y-2">
                <p>
                  <strong>Data Export:</strong> Downloads all your personal data (profile,
                  translations, feedback, corrections, datasets, API keys) as a JSON file,
                  immediately — not emailed to you later.
                </p>
                <p>
                  <strong>Account Deletion:</strong> Your email and password are permanently
                  removed and your account is deactivated. Content you've contributed (reviewed
                  translations, uploaded datasets) stays in the system anonymized, since other
                  parts of the platform legitimately still reference it.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PrivacyDashboard;
