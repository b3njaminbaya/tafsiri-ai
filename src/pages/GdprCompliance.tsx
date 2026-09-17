import { Link } from "react-router-dom";
import PageContainer from "@/components/layout/PageContainer";
import LegalTableOfContents, { type TocEntry } from "@/components/legal/LegalTableOfContents";

const sections: TocEntry[] = [
  { id: "our-commitment-to-gdpr", label: "1. Our Commitment to GDPR" },
  { id: "legal-basis-for-processing", label: "2. Legal Basis for Processing" },
  { id: "your-rights-under-gdpr", label: "3. Your Rights Under GDPR" },
  { id: "data-protection-measures", label: "4. Data Protection Measures" },
  { id: "international-data-transfers", label: "5. International Data Transfers" },
  { id: "data-retention", label: "6. Data Retention" },
  { id: "data-breach-notification", label: "7. Data Breach Notification" },
  { id: "data-protection-contact", label: "8. Data Protection Contact" },
  { id: "how-to-exercise-your-rights", label: "9. How to Exercise Your Rights" },
  { id: "complaints-and-supervisory-authority", label: "10. Complaints and Supervisory Authority" },
  { id: "contact-information", label: "11. Contact Information" },
];

const GdprCompliance = () => {
  return (
    <PageContainer>
      <div className="lg:flex lg:gap-12 lg:items-start max-w-5xl mx-auto">
        <LegalTableOfContents entries={sections} className="lg:order-2" />
        <div className="max-w-4xl mx-auto prose prose-slate dark:prose-invert">
        <h1 className="text-4xl font-bold tracking-tight mb-8">GDPR Compliance</h1>
        <p className="text-muted-foreground mb-8">Last updated: September 17, 2026</p>

        <section id="our-commitment-to-gdpr" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">1. Our Commitment to GDPR</h2>
          <p className="mb-4">We are committed to complying with the General Data Protection Regulation (GDPR) and protecting the privacy rights of individuals in the European Union. This page outlines how we implement GDPR requirements in our neural machine translation platform.</p>
        </section>

        <section id="legal-basis-for-processing" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">2. Legal Basis for Processing</h2>
          <p className="mb-4">We process personal data based on the following legal grounds:</p>
          
          <h3 className="text-xl font-semibold mb-2">Contractual Necessity</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Account creation and management</li>
            <li>Service delivery and translation processing</li>
            <li>Payment processing and billing</li>
            <li>Customer support and technical assistance</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Legitimate Interest</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Service improvement and optimization</li>
            <li>Security monitoring and fraud prevention</li>
            <li>Analytics and usage statistics</li>
            <li>Marketing to existing customers</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Consent</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Marketing communications to prospects</li>
            <li>Optional cookies and tracking</li>
            <li>Third-party integrations</li>
            <li>Research and development participation</li>
          </ul>
        </section>

        <section id="your-rights-under-gdpr" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">3. Your Rights Under GDPR</h2>
          <p className="mb-4">As a data subject, you have the following rights:</p>

          <h3 className="text-xl font-semibold mb-2">Right of Access (Article 15)</h3>
          <p className="mb-4">You can request a copy of all personal data we hold about you, including:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Account information and profile data</li>
            <li>Translation history and usage logs</li>
            <li>Communication records</li>
            <li>Billing and payment information</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Right to Rectification (Article 16)</h3>
          <p className="mb-4">You can request correction of inaccurate or incomplete personal data through your account settings or by contacting us.</p>

          <h3 className="text-xl font-semibold mb-2">Right to Erasure (Article 17)</h3>
          <p className="mb-4">You can request deletion of your personal data in certain circumstances:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>The data is no longer necessary for the original purpose</li>
            <li>You withdraw consent and no other legal basis applies</li>
            <li>The data has been unlawfully processed</li>
            <li>Deletion is required for legal compliance</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Right to Restrict Processing (Article 18)</h3>
          <p className="mb-4">You can request limitation of processing when:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>You contest the accuracy of personal data</li>
            <li>Processing is unlawful but you oppose deletion</li>
            <li>We no longer need the data but you need it for legal claims</li>
            <li>You have objected to processing pending verification</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Right to Data Portability (Article 20)</h3>
          <p className="mb-4">You can receive your personal data in a structured, machine-readable format and transmit it to another service provider.</p>

          <h3 className="text-xl font-semibold mb-2">Right to Object (Article 21)</h3>
          <p className="mb-4">You can object to processing based on legitimate interests or for direct marketing purposes.</p>
        </section>

        <section id="data-protection-measures" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">4. Data Protection Measures</h2>
          <p className="mb-4">Measures actually in place today:</p>

          <ul className="list-disc pl-6 mb-4">
            <li>Traffic between your browser and the API is served over HTTPS/TLS</li>
            <li>Passwords are hashed with bcrypt; API keys are hashed at rest and shown only once, at creation</li>
            <li>Role-based access control (user, translator, admin) enforced server-side on every request</li>
            <li>The web app authenticates via an httpOnly session cookie, not a token readable by JavaScript</li>
          </ul>
          <p className="mb-4">
            We do not currently claim independently audited certifications (SOC 2, ISO 27001) or a
            formal penetration-testing program — see the{" "}
            <Link to="/security" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
              Security page
            </Link>{" "}
            for the full, honest picture.
          </p>
        </section>

        <section id="international-data-transfers" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">5. International Data Transfers</h2>
          <p className="mb-4">
            If you are located outside the region where this service's infrastructure runs, using
            it involves transferring your data internationally. We have not yet formalized Standard
            Contractual Clauses or a Binding Corporate Rules program for these transfers. If this
            matters for your use case, please{" "}
            <Link to="/contact" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
              contact us
            </Link>{" "}
            before relying on this platform for it.
          </p>
        </section>

        <section id="data-retention" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">6. Data Retention</h2>
          <p className="mb-4">
            Account data and translation history are retained for as long as your account is
            active, since your translation history is a core feature you can access at any time —
            we do not delete translations after a fixed period. You can permanently anonymize your
            account and revoke your API keys at any time from the{" "}
            <Link to="/privacy-settings" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
              Privacy Dashboard
            </Link>
            . Billing records, where applicable, are retained by our payment processor (Stripe)
            under its own retention terms.
          </p>
        </section>

        <section id="data-breach-notification" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">7. Data Breach Notification</h2>
          <p className="mb-4">
            In the event of a personal data breach affecting your data, we will notify affected
            users and the relevant supervisory authority as required by applicable law. We do not
            currently operate a dedicated, staffed security incident-response team — see the{" "}
            <Link to="/security" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
              Security page
            </Link>
            .
          </p>
        </section>

        <section id="data-protection-contact" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">8. Data Protection Contact</h2>
          <p className="mb-4">
            We have not designated a formal Data Protection Officer. For any data protection
            question or request, use the contact channel below — a real person reads and responds
            to it.
          </p>
        </section>

        <section id="how-to-exercise-your-rights" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">9. How to Exercise Your Rights</h2>
          <p className="mb-4">To exercise your GDPR rights:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Use the privacy controls in your account dashboard</li>
            <li>Submit a request through the GDPR request form linked below</li>
            <li>
              Or use the{" "}
              <Link to="/contact" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
                contact form
              </Link>
            </li>
          </ul>
          <p className="mb-4">
            Access and portability requests are fulfilled immediately via the real data export in
            your Privacy Dashboard. Other request types are logged and reviewed manually — see{" "}
            <Link to="/gdpr-request" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
              Submit GDPR Request
            </Link>{" "}
            below for what's automated versus what needs a human.
          </p>

          <div className="mt-4">
            <Link
              to="/gdpr-request"
              className="inline-flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Submit GDPR Request
            </Link>
          </div>
        </section>

        <section id="complaints-and-supervisory-authority" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">10. Complaints and Supervisory Authority</h2>
          <p className="mb-4">If you believe we have not handled your personal data properly, you have the right to lodge a complaint with:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Your local supervisory authority</li>
            <li>The Information Commissioner's Office (ICO) if you're in the UK</li>
            <li>The Commission Nationale de l'Informatique et des Libertés (CNIL) if you're in France</li>
            <li>Any other relevant EU data protection authority</li>
          </ul>
        </section>

        <section id="contact-information" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">11. Contact Information</h2>
          <p className="mb-4">For GDPR-related inquiries, please use the{" "}
            <Link to="/contact" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
              contact form
            </Link>
            . We have not designated an EU representative under Article 27 at this time.
          </p>
        </section>
        </div>
      </div>
    </PageContainer>
  );
};

export default GdprCompliance;