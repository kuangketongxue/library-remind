"use client";

import Link from "next/link";
import { useState, useRef, useEffect } from "react";
import { usePathname } from "next/navigation";

const navSections = [
  {
    icon: "🚀",
    label: "快速开始",
    defaultOpen: true,
    items: [
      { href: "/docs", label: "快速开始" },
      { href: "/docs#下载运行", label: "下载运行" },
      { href: "/docs#设定目标", label: "设定目标" },
      { href: "/docs#开始学习", label: "开始学习" },
      { href: "/docs#复盘追踪", label: "复盘追踪" },
    ],
  },
  {
    icon: "📚",
    label: "功能说明",
    defaultOpen: false,
    items: [
      { href: "/docs#60分钟循环", label: "60 分钟专注循环" },
      { href: "/docs#护眼提醒", label: "20-20-20 护眼提醒" },
      { href: "/docs#学习追踪", label: "学习时长追踪" },
      { href: "/docs#趋势分析", label: "趋势分析" },
      { href: "/docs#ai分析", label: "AI 学习分析" },
    ],
  },
  {
    icon: "📋",
    label: "更新日志",
    defaultOpen: false,
    items: [
      { href: "/docs#更新日志", label: "版本历史" },
    ],
  },
  {
    icon: "❓",
    label: "常见问题",
    defaultOpen: false,
    items: [
      { href: "/docs#常见问题", label: "FAQ" },
    ],
  },
];

export default function DocsNav() {
  const pathname = usePathname();
  const [openSections, setOpenSections] = useState<Record<string, boolean>>(() => {
    const init: Record<string, boolean> = {};
    for (const s of navSections) {
      init[s.label] = s.defaultOpen;
    }
    return init;
  });
  const [searchQuery, setSearchQuery] = useState("");
  const navRef = useRef<HTMLDivElement>(null);

  const toggleSection = (label: string) => {
    setOpenSections((prev) => ({ ...prev, [label]: !prev[label] }));
  };

  const filteredSections = navSections
    .map((section) => ({
      ...section,
      items: section.items.filter((item) =>
        item.label.toLowerCase().includes(searchQuery.toLowerCase())
      ),
    }))
    .filter((section) => section.items.length > 0);

  return (
    <aside
      ref={navRef}
      className="w-56 shrink-0 sticky top-20 h-[calc(100vh-5rem)] overflow-y-auto py-6 hidden lg:block"
    >
      {/* Search */}
      <div className="px-3 mb-4">
        <div className="relative">
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--fg-muted)]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            placeholder="搜索文档..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[var(--surface-raised)] border border-[var(--border)] rounded-lg pl-9 pr-8 py-2 text-xs text-[var(--fg)] placeholder:text-[var(--fg-muted)] focus:outline-none focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] transition-colors"
          />
          <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-[var(--fg-muted)] bg-[var(--surface)] px-1.5 py-0.5 rounded border border-[var(--border)] font-mono">
            ⌘K
          </kbd>
        </div>
      </div>

      {/* Navigation sections */}
      <nav className="px-3 space-y-0.5">
        {filteredSections.map((section) => {
          const isOpen = openSections[section.label];
          return (
            <div key={section.label} className="mb-1">
              <button
                onClick={() => toggleSection(section.label)}
                className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium text-[var(--fg-dim)] hover:text-[var(--fg)] hover:bg-[var(--surface)] transition-colors"
              >
                <span className="text-base">{section.icon}</span>
                <span className="flex-1 text-left">{section.label}</span>
                <svg
                  className={`w-3.5 h-3.5 transition-transform duration-200 ${
                    isOpen ? "rotate-180" : ""
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>

              {isOpen && (
                <div className="ml-1.5 pl-4 border-l border-[var(--border)] space-y-0.5 mt-0.5">
                  {section.items.map((item) => {
                    const itemPath = item.href.split("#")[0];
                    const isActive = pathname === itemPath;
                    return (
                      <a
                        key={item.href}
                        href={item.href}
                        className={`block text-[13px] px-3 py-1.5 rounded-md transition-colors ${
                          isActive
                            ? "text-[var(--accent)] bg-[var(--accent-soft)] font-medium"
                            : "text-[var(--fg-dim)] hover:text-[var(--fg)] hover:bg-[var(--surface)]"
                        }`}
                      >
                        {item.label}
                      </a>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
