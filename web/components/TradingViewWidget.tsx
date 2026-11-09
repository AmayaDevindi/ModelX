"use client";

// Embeds TradingView's own free Advanced Chart widget for a CSE-listed
// symbol. The CSE has an official data partnership with TradingView, and
// its symbol format matches ours exactly with a "CSELK:" prefix (e.g. our
// "JKH.N0000" is TradingView's "CSELK:JKH.N0000") - confirmed by checking
// real TradingView symbol pages before building this, not assumed.
import { useEffect, useRef } from "react";

export default function TradingViewWidget({ symbol }: { symbol: string }) {
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!container.current) return;
    container.current.innerHTML = "";

    const widgetDiv = document.createElement("div");
    widgetDiv.className = "tradingview-widget-container__widget";
    widgetDiv.style.height = "100%";
    widgetDiv.style.width = "100%";
    container.current.appendChild(widgetDiv);

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: `CSELK:${symbol}`,
      interval: "D",
      timezone: "Asia/Colombo",
      theme: "dark",
      style: "1",
      locale: "en",
      enable_publishing: false,
      allow_symbol_change: false,
      calendar: false,
      hide_top_toolbar: false,
      support_host: "https://www.tradingview.com",
    });
    container.current.appendChild(script);
  }, [symbol]);

  return (
    <div
      className="tradingview-widget-container w-full h-[420px] border border-border rounded overflow-hidden"
      ref={container}
    />
  );
}
