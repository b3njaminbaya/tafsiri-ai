import { Link } from "react-router-dom";

const Accessibility = () => {
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-4xl mx-auto prose prose-slate dark:prose-invert">
        <h1 className="text-4xl font-bold tracking-tight mb-8">Accessibility Statement</h1>
        <p className="text-muted-foreground mb-8">Last updated: January 18, 2025</p>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Our Commitment to Accessibility</h2>
          <p className="mb-4">We are committed to ensuring that our neural machine translation platform is accessible to everyone, including users with disabilities. We strive to comply with the Web Content Accessibility Guidelines (WCAG) 2.1 Level AA standards.</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Accessibility Features</h2>
          
          <h3 className="text-xl font-semibold mb-2">Keyboard Navigation</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Full keyboard navigation support for all interactive elements</li>
            <li>Visible focus indicators on all focusable elements</li>
            <li>Logical tab order throughout the interface</li>
            <li>Skip links to bypass repetitive content</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Screen Reader Support</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Semantic HTML markup for proper structure</li>
            <li>ARIA labels and descriptions for complex UI components</li>
            <li>Live regions for dynamic content updates</li>
            <li>Alternative text for all informative images</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Visual Accessibility</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>High contrast color scheme options</li>
            <li>Minimum 4.5:1 color contrast ratio for normal text</li>
            <li>Minimum 3:1 contrast ratio for large text and UI components</li>
            <li>Scalable fonts that work well up to 200% zoom</li>
            <li>Dark mode option for light sensitivity</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Motor Accessibility</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Large click targets (minimum 44x44 pixels)</li>
            <li>Adequate spacing between interactive elements</li>
            <li>Drag and drop alternatives</li>
            <li>Time limits can be extended or disabled</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Assistive Technology Compatibility</h2>
          <p className="mb-4">Our platform is tested with the following assistive technologies:</p>
          
          <h3 className="text-xl font-semibold mb-2">Screen Readers</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>NVDA (Windows)</li>
            <li>JAWS (Windows)</li>
            <li>VoiceOver (macOS/iOS)</li>
            <li>TalkBack (Android)</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Voice Control</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Dragon NaturallySpeaking (Windows)</li>
            <li>Voice Control (macOS/iOS)</li>
            <li>Voice Access (Android)</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2">Browser Compatibility</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Chrome, Firefox, Safari, and Edge (latest versions)</li>
            <li>Mobile browsers on iOS and Android</li>
            <li>Browser zoom up to 400% without horizontal scrolling</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Known Limitations</h2>
          <p className="mb-4">We are continuously working to improve accessibility. Current known limitations include:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Some complex data visualizations may have limited screen reader support</li>
            <li>PDF documents may not be fully accessible (we're working on HTML alternatives)</li>
            <li>Third-party integrations may not meet our full accessibility standards</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Accessibility Testing</h2>
          <p className="mb-4">
            The interface is built on shadcn/ui components, which follow the underlying Radix UI
            primitives' accessibility patterns (keyboard navigation, ARIA attributes, focus
            management) by default. We do not yet run a dedicated automated accessibility test
            suite or a formal third-party audit program — if you encounter a barrier, please report
            it using the contact method below so we can fix it.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Getting Help</h2>
          <p className="mb-4">If you encounter any accessibility barriers while using our platform, please let us know:</p>
          
          <h3 className="text-xl font-semibold mb-2">Contact Methods</h3>
          <p className="mb-4">
            Use the{" "}
            <Link to="/contact" className="text-primary underline">
              contact form
            </Link>{" "}
            to report an accessibility barrier.
          </p>

          <h3 className="text-xl font-semibold mb-2">Information to Include</h3>
          <ul className="list-disc pl-6 mb-4">
            <li>Description of the accessibility barrier</li>
            <li>Your operating system and browser</li>
            <li>Assistive technology you're using (if any)</li>
            <li>Steps to reproduce the issue</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Alternative Formats</h2>
          <p className="mb-4">We can provide information in alternative formats upon request:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Large print documents</li>
            <li>Audio recordings</li>
            <li>Plain text versions</li>
            <li>Braille (with advance notice)</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Training and Awareness</h2>
          <p className="mb-4">Our team receives regular training on accessibility best practices:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Developers trained on WCAG guidelines and implementation</li>
            <li>Designers educated on inclusive design principles</li>
            <li>Content creators trained on accessible content creation</li>
            <li>Customer support trained on assistive technology basics</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Continuous Improvement</h2>
          <p className="mb-4">We are committed to ongoing accessibility improvements through:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Regular accessibility audits and testing</li>
            <li>User feedback and testing with the disability community</li>
            <li>Staying updated with accessibility standards and best practices</li>
            <li>Integration of accessibility considerations in our development process</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Third-Party Content</h2>
          <p className="mb-4">While we work to ensure our platform is accessible, we cannot always guarantee the accessibility of third-party content or services integrated into our platform. We encourage our partners to meet accessibility standards and will work with them to address any issues.</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Feedback and Complaints</h2>
          <p className="mb-4">Your feedback helps us improve. If you encounter accessibility issues or have suggestions for improvement, please contact us using the methods listed above. We will:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Acknowledge your feedback within 2 business days</li>
            <li>Investigate the issue thoroughly</li>
            <li>Provide a timeline for resolution</li>
            <li>Keep you updated on our progress</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Resources</h2>
          <p className="mb-4">For more information about web accessibility:</p>
          <ul className="list-disc pl-6 mb-4">
            <li>Web Content Accessibility Guidelines (WCAG) 2.1</li>
            <li>Web Accessibility Initiative (WAI)</li>
            <li>Americans with Disabilities Act (ADA)</li>
            <li>Section 508 Standards</li>
          </ul>
        </section>
      </div>
    </div>
  );
};

export default Accessibility;