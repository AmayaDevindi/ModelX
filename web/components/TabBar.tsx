// The tab row across the top of the terminal shell. PLAN is the only real
// tab right now - the rest are listed so the shape of the final product is
// visible, but are not clickable yet.
const TABS = [
  { key: "PLAN", label: "PLAN", soon: false },
  { key: "MKTS", label: "MKTS", soon: true },
  { key: "QUOTE", label: "QUOTE", soon: true },
  { key: "FA", label: "FA", soon: true },
  { key: "RISK", label: "RISK", soon: true },
  { key: "NEWS", label: "NEWS", soon: true },
  { key: "ECO", label: "ECO", soon: true },
];

export default function TabBar() {
  return (
    <nav className="flex items-center gap-1 border-b border-border px-4 overflow-x-auto">
      {TABS.map((tab) => (
        <div
          key={tab.key}
          className={[
            "flex items-center gap-1.5 px-3 py-2.5 text-sm tracking-wide select-none whitespace-nowrap",
            tab.soon
              ? "text-muted cursor-default"
              : "text-accent border-b-2 border-accent font-medium",
          ].join(" ")}
        >
          {tab.label}
          {tab.soon && (
            <span className="text-[10px] text-muted/70 border border-border rounded px-1 py-0.5 leading-none">
              soon
            </span>
          )}
        </div>
      ))}
    </nav>
  );
}
