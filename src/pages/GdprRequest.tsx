import { Link } from 'react-router-dom';
import PageContainer from "@/components/layout/PageContainer";
import GdprRequestForm from '@/components/GdprRequestForm';

const GdprRequest = () => {
  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-4">GDPR Data Request</h1>
          <p className="text-muted-foreground text-lg">
            Exercise your rights under the General Data Protection Regulation
          </p>
        </div>

        <GdprRequestForm />

        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>
            Need help?{' '}
            <Link to="/contact" className="text-brand hover:underline">
              Contact us
            </Link>
          </p>
        </div>
      </div>
    </PageContainer>
  );
};

export default GdprRequest;