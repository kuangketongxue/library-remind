"use client";

import { useState, useEffect } from "react";

export default function StickyCTA() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 600);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className={`sticky-cta ${visible ? "visible" : ""}`}>
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-full bg-[var(--accent)] flex items-center justify-center text-[var(--bg)] text-[10px] font-bold font-display">R</div>
          <span className="text-sm font-medium hidden sm:block">Rest Reminder</span>
        </div>
        <a
          href="#download"
          className="btn-primary px-5 py-2 text-sm"
        >
          免费下载
        </a>
      </div>
    </div>
  );
}
