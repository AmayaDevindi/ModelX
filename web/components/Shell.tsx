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

      <TabBar />

      <main className="flex-1 flex flex-col items-center p-8">{children}</main>
    </div>
  );
}
