import { Suspense } from "react";
import TabBar from "@/components/TabBar";

export default function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col flex-1">
      <header className="flex items-center justify-between px-4 py-3 border-b border-border">
        <div className="flex items-baseline gap-2">
          <span className="text-accent font-semibold tracking-tight">ModelX</span>
          <span className="text-muted text-xs">Sri Lanka investment terminal</span>
        </div>
        <span className="text-muted text-xs">education only &middot; not financial advice</span>
      </header>

      {/* TabBar reads the current URL (usePathname) to highlight the active
          tab, which is only known at request time - Suspense lets the rest
          of the page prerender while that one piece streams in. */}
      <Suspense fallback={<div className="h-[41px] border-b border-border" />}>
        <TabBar />
      </Suspense>

      <main className="flex-1 flex flex-col items-center p-8">{children}</main>
    </div>
  );
}
