"use client";

// The tab row across the top of the terminal shell. PLAN, FA and NEWS are
// real pages now; the rest are listed so the shape of the final product is
// visible, but aren't built yet.
import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { key: "PLAN", label: "PLAN", href: "/" },
  { key: "MKTS", label: "MKTS", soon: true },
  { key: "QUOTE", label: "QUOTE", href: "/quote" },
  { key: "FA", label: "FA", href: "/fa" },
  { key: "RISK", label: "RISK", soon: true },
  { key: "NEWS", label: "NEWS", href: "/news" },
  { key: "ECO", label: "ECO", soon: true },
];

export default function TabBar() {
  const pathname = usePathname();

  return (
    <nav className="flex items-center gap-1 border-b border-border px-4 overflow-x-auto">
      {TABS.map((tab) => {
        const active = tab.href && (pathname === tab.href || pathname.startsWith(tab.href + "/"));
        if (tab.soon) {
          return (
            <div
              key={tab.key}
              className="flex items-center gap-1.5 px-3 py-2.5 text-sm tracking-wide select-none whitespace-nowrap text-muted cursor-default"
            >
              {tab.label}
              <span className="text-[10px] text-muted/70 border border-border rounded px-1 py-0.5 leading-none">
                soon
              </span>
            </div>
          );
        }
        return (
          <Link
            key={tab.key}
            href={tab.href!}
            className={[
              "flex items-center gap-1.5 px-3 py-2.5 text-sm tracking-wide whitespace-nowrap",
              active ? "text-accent border-b-2 border-accent font-medium" : "text-muted hover:text-foreground",
            ].join(" ")}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
