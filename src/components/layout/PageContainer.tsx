import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface PageContainerProps {
  children: ReactNode;
  className?: string;
}

// The single width/padding source of truth every non-landing page opts
// into, matching NavBar/Footer's own `container` usage — see the UI/UX
// overhaul plan for why this is an opt-in component rather than a wrapper
// around App.tsx's <main>: Index.tsx's full-bleed section backgrounds would
// break if <main> itself were width-constrained.
const PageContainer = ({ children, className }: PageContainerProps) => (
  <div className={cn("container py-16", className)}>{children}</div>
);

export default PageContainer;
