import { Link } from "react-router-dom";

const TermsOfService = () => {
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-4xl mx-auto prose prose-slate dark:prose-invert">
        <h1 className="text-4xl font-bold tracking-tight mb-8">Terms of Service</h1>
        <p className="text-muted-foreground mb-8">Last updated: January 18, 2025</p>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">1. Acceptance of Terms</h2>
          <p className="mb-4">By accessing or using our neural machine translation platform ("Service"), you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, you may not use our Service.</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">2. Description of Service</h2>
          <p className="mb-4">Our Service provides neural machine translation capabilities through a web interface and API. The Service includes:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Real-time text translation between multiple languages</li>
            <li>Batch translation capabilities</li>
            <li>Custom model training and deployment</li>
            <li>Translation analytics and quality metrics</li>
            <li>API access for integration into third-party applications</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">3. User Accounts and Registration</h2>
          <p className="mb-4">To use certain features of our Service, you must create an account. You agree to:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Provide accurate and complete registration information</li>
            <li>Maintain the security of your account credentials</li>
            <li>Notify us immediately of any unauthorized use of your account</li>
            <li>Accept responsibility for all activities under your account</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">4. Acceptable Use Policy</h2>
          <p className="mb-4">You agree not to use our Service to:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Violate any applicable laws or regulations</li>
            <li>Transmit harmful, offensive, or illegal content</li>
            <li>Attempt to reverse engineer or compromise our systems</li>
            <li>Exceed API rate limits or abuse our infrastructure</li>
            <li>Infringe on intellectual property rights of others</li>
            <li>Share your account access with unauthorized users</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">5. Billing and Payment</h2>
          <p className="mb-4">For paid plans:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Fees are billed in advance on a monthly or annual basis</li>
            <li>Usage-based charges are calculated and billed monthly</li>
            <li>All fees are non-refundable except as required by law</li>
            <li>We may change our pricing with 30 days' notice</li>
            <li>Accounts may be suspended for non-payment</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">6. Intellectual Property</h2>
          <p className="mb-4">The Service and its original content, features, and functionality are owned by us and are protected by international copyright, trademark, and other intellectual property laws.</p>
          <p className="mb-4">You retain ownership of any content you submit to our Service, but grant us a license to process, store, and transmit such content as necessary to provide the Service.</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">7. Data Privacy and Security</h2>
          <p className="mb-4">We are committed to protecting your privacy and data security:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>We encrypt all data in transit and at rest</li>
            <li>We do not use your translation data to improve our models without consent</li>
            <li>We comply with applicable data protection regulations</li>
            <li>You may request deletion of your data at any time</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">8. Service Availability and Support</h2>
          <p className="mb-4">We strive to maintain high service availability but cannot guarantee uninterrupted access. We provide:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>99.9% uptime SLA for paid plans</li>
            <li>Email support for all users</li>
            <li>Priority support for enterprise customers</li>
            <li>Regular maintenance windows with advance notice</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">9. Limitation of Liability</h2>
          <p className="mb-4">To the maximum extent permitted by law, we shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses.</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">10. Termination</h2>
          <p className="mb-4">We may terminate or suspend your account and access to the Service immediately, without prior notice or liability, for any reason, including without limitation if you breach the Terms.</p>
          <p className="mb-4">You may terminate your account at any time by contacting us or using account deletion features in your dashboard.</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">11. Changes to Terms</h2>
          <p className="mb-4">We reserve the right to modify or replace these Terms at any time. We will provide notice of material changes by posting on our website or sending you an email.</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">12. Governing Law</h2>
          <p className="mb-4">These Terms shall be governed by the laws of the State of California, without regard to its conflict of law provisions. Any disputes shall be resolved in the courts of San Francisco County, California.</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">13. Contact Information</h2>
          <p className="mb-4">
            For questions about these Terms, please use the{" "}
            <Link to="/contact" className="text-primary underline">
              contact form
            </Link>
            .
          </p>
        </section>
      </div>
    </div>
  );
};

export default TermsOfService;