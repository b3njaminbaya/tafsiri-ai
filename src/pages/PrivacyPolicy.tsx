import { Link } from "react-router-dom";
import PageContainer from "@/components/layout/PageContainer";
import LegalTableOfContents, { type TocEntry } from "@/components/legal/LegalTableOfContents";

const sections: TocEntry[] = [
  { id: "information-we-collect", label: "1. Information We Collect" },
  { id: "how-we-use-your-information", label: "2. How We Use Your Information" },
  { id: "data-retention-and-security", label: "3. Data Retention and Security" },
  { id: "data-sharing-and-disclosure", label: "4. Data Sharing and Disclosure" },
  { id: "your-rights-and-choices", label: "5. Your Rights and Choices" },
  { id: "international-data-transfers", label: "6. International Data Transfers" },
  { id: "childrens-privacy", label: "7. Children's Privacy" },
  { id: "changes-to-this-policy", label: "8. Changes to This Policy" },
  { id: "contact-us", label: "9. Contact Us" },
];

const PrivacyPolicy = () => {
  return (
    <PageContainer>
      <div className="lg:flex lg:gap-12 lg:items-start max-w-5xl mx-auto">
        <LegalTableOfContents entries={sections} className="lg:order-2" />
        <div className="max-w-4xl mx-auto prose prose-slate dark:prose-invert">
        <h1 className="text-4xl font-bold tracking-tight mb-8">Privacy Policy</h1>
        <p className="text-muted-foreground mb-8">Last updated: September 18, 2026</p>

        <section id="information-we-collect" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">1. Information We Collect</h2>
          <p className="mb-4">We collect information you provide directly to us, such as when you create an account, use our translation services, or contact us for support.</p>
          
          <h3 className="text-xl font-semibold mb-2">Personal Information</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Account information (email, username, password)</li>
            <li>Profile information (name, company, preferences)</li>
            <li>Billing information (payment details, billing address)</li>
            <li>Communication records (support tickets, feedback)</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Usage Information</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Translation requests and responses</li>
            <li>API usage metrics and analytics</li>
            <li>Device and browser information</li>
            <li>IP address and location data</li>
          </ul>
        </section>

        <section id="how-we-use-your-information" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">2. How We Use Your Information</h2>
          <p className="mb-4">We use the information we collect to:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Provide and improve our translation services</li>
            <li>Process payments and manage your account</li>
            <li>Send service updates and security notifications</li>
            <li>Respond to your questions and provide support</li>
            <li>Analyze usage patterns to enhance our platform</li>
            <li>Comply with legal obligations and prevent fraud</li>
          </ul>
        </section>

        <section id="data-retention-and-security" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">3. Data Retention and Security</h2>
          <p className="mb-4">We implement industry-standard security measures to protect your personal information:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>End-to-end encryption for all data transmission</li>
            <li>Secure data centers with 24/7 monitoring</li>
            <li>Regular security audits and penetration testing</li>
            <li>SOC 2 Type II compliance certification</li>
          </ul>
          <p className="mb-4">We retain your personal information only as long as necessary to provide our services or as required by law.</p>
        </section>

        <section id="data-sharing-and-disclosure" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">4. Data Sharing and Disclosure</h2>
          <p className="mb-4">We do not sell, rent, or share your personal information with third parties except:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>With your explicit consent</li>
            <li>To comply with legal obligations or court orders</li>
            <li>To protect our rights, property, or safety</li>
            <li>With trusted service providers under strict confidentiality agreements</li>
            <li>In connection with a merger, acquisition, or sale of assets</li>
          </ul>
        </section>

        <section id="your-rights-and-choices" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">5. Your Rights and Choices</h2>
          <p className="mb-4">You have the right to:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Access and update your personal information</li>
            <li>Request deletion of your data (subject to legal requirements)</li>
            <li>Opt out of marketing communications</li>
            <li>Export your data in a portable format</li>
            <li>Lodge a complaint with relevant data protection authorities</li>
          </ul>
        </section>

        <section id="international-data-transfers" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">6. International Data Transfers</h2>
          <p className="mb-4">Your information may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place, including:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Standard contractual clauses approved by the European Commission</li>
            <li>Adequacy decisions for data transfers</li>
            <li>Certification under Privacy Shield or similar frameworks</li>
          </ul>
        </section>

        <section id="childrens-privacy" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">7. Children's Privacy</h2>
          <p className="mb-4">Our services are not intended for children under 13. We do not knowingly collect personal information from children under 13. If we become aware that we have collected such information, we will delete it promptly.</p>
        </section>

        <section id="changes-to-this-policy" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">8. Changes to This Policy</h2>
          <p className="mb-4">We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the new policy on our website and sending you a notification.</p>
        </section>

        <section id="contact-us" className="mb-8 scroll-mt-24">
          <h2 className="text-2xl font-semibold mb-4">9. Contact Us</h2>
          <p className="mb-4">
            If you have any questions about this Privacy Policy, please use the{" "}
            <Link to="/contact" className="text-brand underline underline-offset-4 hover:text-brand/80 transition-colors">
              contact form
            </Link>
            .
          </p>
        </section>
        </div>
      </div>
    </PageContainer>
  );
};

export default PrivacyPolicy;