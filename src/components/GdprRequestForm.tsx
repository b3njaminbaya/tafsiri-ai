import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Shield, Download, Trash2, Edit, Eye, Ban, FileText, Clock, CheckCircle2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { api, ApiError, type GdprRequestRecord, type GdprRequestType } from '@/lib/api';

const requestTypes: { value: GdprRequestType; label: string; description: string; icon: typeof Eye }[] = [
  {
    value: 'access',
    label: 'Right of Access',
    description: 'Request a copy of all personal data we hold about you — fulfilled immediately via your Privacy Dashboard export.',
    icon: Eye,
  },
  {
    value: 'rectification',
    label: 'Right to Rectification',
    description: 'Request correction of inaccurate or incomplete personal data',
    icon: Edit,
  },
  {
    value: 'erasure',
    label: 'Right to Erasure',
    description: 'Request deletion of your personal data — you can also do this immediately from your Privacy Dashboard.',
    icon: Trash2,
  },
  {
    value: 'restrict',
    label: 'Right to Restrict Processing',
    description: 'Request limitation of how we process your data',
    icon: Ban,
  },
  {
    value: 'portability',
    label: 'Right to Data Portability',
    description: 'Request your data in a portable format — fulfilled immediately via your Privacy Dashboard export.',
    icon: Download,
  },
  {
    value: 'object',
    label: 'Right to Object',
    description: 'Object to processing based on legitimate interests or marketing',
    icon: Shield,
  },
];

const GdprRequestForm = () => {
  const { toast } = useToast();
  const [requestType, setRequestType] = useState<GdprRequestType>('access');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [history, setHistory] = useState<GdprRequestRecord[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  const loadHistory = () => {
    api
      .listGdprRequests()
      .then(setHistory)
      .catch(() => undefined)
      .finally(() => setLoadingHistory(false));
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await api.submitGdprRequest({ request_type: requestType, description: description || undefined });
      toast({
        title: 'Request submitted',
        description: 'Your GDPR request has been recorded.',
      });
      setDescription('');
      loadHistory();
    } catch (error) {
      toast({
        title: 'Submission failed',
        description: error instanceof ApiError ? error.message : String(error),
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedRequestType = requestTypes.find((type) => type.value === requestType);
  const IconComponent = selectedRequestType?.icon ?? FileText;

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <Shield className="h-6 w-6 text-primary" />
            <div>
              <CardTitle>GDPR Data Request</CardTitle>
              <CardDescription>
                Submit a request to exercise your data protection rights under GDPR
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-3">
              <Label>Type of Request</Label>
              <Select value={requestType} onValueChange={(value: GdprRequestType) => setRequestType(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {requestTypes.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      <div className="flex items-center gap-2">
                        <type.icon className="h-4 w-4" />
                        {type.label}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {selectedRequestType && (
                <Alert>
                  <IconComponent className="h-4 w-4" />
                  <AlertDescription>{selectedRequestType.description}</AlertDescription>
                </Alert>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Additional Details</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Provide any additional details about your request..."
                rows={4}
              />
            </div>

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? 'Submitting Request...' : 'Submit GDPR Request'}
            </Button>
          </form>

          <div className="mt-6 p-4 bg-muted rounded-lg">
            <h4 className="font-medium mb-2">Need Help?</h4>
            <p className="text-sm text-muted-foreground mb-2">
              If you need assistance with your request, you can also{" "}
              <Link to="/contact" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
                contact us
              </Link>
              .
            </p>
          </div>
        </CardContent>
      </Card>

      {!loadingHistory && history.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Your Request History</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {history.map((req) => (
              <div key={req.id} className="flex items-center justify-between border-b pb-3 last:border-0 last:pb-0">
                <div>
                  <div className="font-medium capitalize">{req.request_type}</div>
                  <div className="text-xs text-muted-foreground">
                    {new Date(req.created_at).toLocaleString()}
                  </div>
                </div>
                <Badge variant={req.status === 'completed' ? 'default' : 'secondary'} className="flex items-center gap-1">
                  {req.status === 'completed' ? (
                    <CheckCircle2 className="h-3 w-3" />
                  ) : (
                    <Clock className="h-3 w-3" />
                  )}
                  {req.status}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default GdprRequestForm;
