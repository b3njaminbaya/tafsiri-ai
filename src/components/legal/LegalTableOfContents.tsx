import { useState } from "react";
import { ChevronDown, List } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";

export interface TocEntry {
  id: string;
  label: string;
}

interface LegalTableOfContentsProps {
  entries: TocEntry[];
  className?: string;
}

// Jump-to-section nav for the legal-page template (Privacy, Terms, Cookie
// Policy, GDPR, Accessibility). Desktop: sticky sidebar column. Mobile: a
// collapsible disclosure above the content, since there's no room for a
// side column at narrow widths.
const LegalTableOfContents = ({ entries, className }: LegalTableOfContentsProps) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const list = (onNavigate?: () => void) => (
    <ul className="space-y-1 text-sm">
      {entries.map((entry) => (
        <li key={entry.id}>
          <a
            href={`#${entry.id}`}
            onClick={onNavigate}
            className="block rounded-md px-3 py-1.5 text-muted-foreground hover:text-brand hover:bg-accent transition-colors"
          >
            {entry.label}
          </a>
        </li>
      ))}
    </ul>
  );

  return (
    <>
      {/* Mobile: collapsible disclosure */}
      <div className={cn("lg:hidden mb-8", className)}>
        <Collapsible open={mobileOpen} onOpenChange={setMobileOpen}>
          <CollapsibleTrigger className="flex w-full items-center justify-between rounded-md border px-4 py-3 text-sm font-medium">
            <span className="flex items-center gap-2">
              <List className="h-4 w-4" />
              On this page
            </span>
            <ChevronDown className={cn("h-4 w-4 transition-transform", mobileOpen && "rotate-180")} />
          </CollapsibleTrigger>
          <CollapsibleContent className="border border-t-0 rounded-b-md px-2 py-2">
            {list(() => setMobileOpen(false))}
          </CollapsibleContent>
        </Collapsible>
      </div>

      {/* Desktop: sticky sidebar column */}
      <nav
        aria-label="Table of contents"
        className={cn("hidden lg:block w-56 shrink-0 sticky top-24 self-start", className)}
      >
        <p className="px-3 mb-2 text-sm font-semibold">On this page</p>
        {list()}
      </nav>
    </>
  );
};

export default LegalTableOfContents;
