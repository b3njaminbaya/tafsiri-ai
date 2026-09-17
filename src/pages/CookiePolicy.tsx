import { Link } from "react-router-dom";

const CookiePolicy = () => {
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-4xl mx-auto prose prose-slate dark:prose-invert">
        <h1 className="text-4xl font-bold tracking-tight mb-8">Cookie Policy</h1>
        <p className="text-muted-foreground mb-8">Last updated: January 18, 2025</p>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">1. What Are Cookies</h2>
          <p className="mb-4">Cookies are small text files that are placed on your device when you visit our website. They help us provide you with a better experience by remembering your preferences and enabling certain features.</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">2. Types of Cookies We Use</h2>
          
          <h3 className="text-xl font-semibold mb-2">Essential Cookies</h3>
          <p className="mb-4">These cookies are necessary for the website to function properly:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Session management and authentication</li>
            <li>Security and fraud prevention</li>
            <li>Load balancing and performance optimization</li>
            <li>API rate limiting and usage tracking</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Analytics Cookies</h3>
          <p className="mb-4">These cookies help us understand how visitors interact with our website:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Google Analytics for usage statistics</li>
            <li>Page view tracking and user journey analysis</li>
            <li>Performance monitoring and error tracking</li>
            <li>Feature usage and A/B testing</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Functional Cookies</h3>
          <p className="mb-4">These cookies enable enhanced functionality and personalization:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Language and region preferences</li>
            <li>Theme and display settings</li>
            <li>Recently used translation pairs</li>
            <li>Dashboard customization preferences</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Marketing Cookies</h3>
          <p className="mb-4">These cookies are used to deliver relevant advertisements:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Tracking pixels for retargeting campaigns</li>
            <li>Social media integration cookies</li>
            <li>Conversion tracking for marketing campaigns</li>
            <li>Interest-based advertising preferences</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">3. Third-Party Cookies</h2>
          <p className="mb-4">We use several third-party services that may place cookies on your device:</p>
          
          <h3 className="text-xl font-semibold mb-2">Google Services</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Google Analytics for website analytics</li>
            <li>Google Ads for advertising and remarketing</li>
            <li>Google reCAPTCHA for spam protection</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Social Media Platforms</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Twitter for social sharing and authentication</li>
            <li>LinkedIn for professional networking features</li>
            <li>GitHub for developer authentication</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Payment Processors</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Stripe for secure payment processing</li>
            <li>PayPal for alternative payment methods</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">4. Managing Your Cookie Preferences</h2>
          <p className="mb-4">You can control and manage cookies in several ways:</p>

          <h3 className="text-xl font-semibold mb-2">Browser Settings</h3>
          <p className="mb-4">Most browsers allow you to:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>View and delete existing cookies</li>
            <li>Block all cookies or only third-party cookies</li>
            <li>Set up alerts when cookies are being sent</li>
            <li>Clear cookies when you close the browser</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Cookie Banner</h3>
          <p className="mb-4">When you first visit our website, you'll see a cookie banner allowing you to:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Accept all cookies</li>
            <li>Reject non-essential cookies</li>
            <li>Customize your preferences by cookie type</li>
            <li>Access detailed information about each cookie category</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Opt-Out Links</h3>
          <p className="mb-4">You can opt out of certain third-party cookies:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Google Analytics Opt-out Browser Add-on</li>
            <li>Digital Advertising Alliance opt-out page</li>
            <li>Network Advertising Initiative opt-out page</li>
            <li>Your Online Choices (European users)</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">5. Impact of Disabling Cookies</h2>
          <p className="mb-4">If you choose to disable cookies, some features may not work properly:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>You may need to re-enter login credentials frequently</li>
            <li>Your language and preference settings may not be saved</li>
            <li>Some interactive features may not function correctly</li>
            <li>We won't be able to provide personalized recommendations</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">6. Cookie Retention Periods</h2>
          <p className="mb-4">Different cookies are stored for different periods:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Session cookies: Deleted when you close your browser</li>
            <li>Persistent cookies: Stored for periods ranging from 30 days to 2 years</li>
            <li>Analytics cookies: Typically stored for 26 months</li>
            <li>Marketing cookies: Usually stored for 30-90 days</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">7. Updates to This Policy</h2>
          <p className="mb-4">We may update this Cookie Policy from time to time to reflect changes in our practices or legal requirements. We will notify you of any material changes by posting the updated policy on our website.</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">8. Contact Us</h2>
          <p className="mb-4">
            If you have questions about our use of cookies, please use the{" "}
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

export default CookiePolicy;