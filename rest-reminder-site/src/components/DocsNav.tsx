"use client";

import Link from "next/link";
import { useState, useRef, useEffect } from "react";
import { usePathname } from "next/navigation";
import { useI18n } from "@/lib/i18n";

const navSections = [
  {
    icon: "🚀",
    labelKey: "docs.quick_start",
    defaultOpen: true,
    items: [
      { href: "/docs", labelKey: "docs.quick_start" },
      { href: "/docs#下载运行", labelKey: "docs.download_run" },
      { href: "/docs#设定目标", labelKey: "docs.set_goal" },
      { href: "/docs#开始学习", labelKey: "docs.start_learn" },
      { href: "/docs#复盘追踪", labelKey: "docs.review_track" },
    ],
  },
  {
    icon: "📚",
    labelKey: "docs.features",
    defaultOpen: false,
    items: [
      { href: "/docs#专注循环", labelKey: "docs.focus_cycle" },
      { href: "/docs#护眼提醒", labelKey: "docs.eye_care" },
      { href: "/docs#学习追踪", labelKey: "docs.learning_track" },
      { href: "/docs#趋势分析", labelKey: "docs.trends" },
      { href: "/docs#ai分析", labelKey: "docs.ai_analysis" },
    ],
  },
  {
    icon: "⚙",
    labelKey: "docs.settings",
    defaultOpen: false,
    items: [
      { href: "/docs#设置详解", labelKey: "docs.settings_detail" },
    ],
  },
  {
    icon: "📋",
    labelKey: "docs.changelog",
    defaultOpen: false,
    items: [
      { href: "/docs#更新日志", labelKey: "docs.history" },
    ],
  },
  {
    icon: "❓",
    labelKey: "docs.faq",
    defaultOpen: false,
    items: [
      { href: "/docs#常见问题", labelKey: "docs.faq_items" },
    ],
  },
  {
    icon: "🔧",
    labelKey: "docs.troubleshoot",
    defaultOpen: false,
    items: [
      { href: "/docs#故障排除", labelKey: "docs.troubleshoot_items" },
    ],
  },
  {
    icon: "🛡",
    labelKey: "docs.legal",
    defaultOpen: false,
    items: [
      { href: "/privacy", labelKey: "footer.link_privacy" },
      { href: "/terms", labelKey: "footer.link_terms" },
      { href: "/rules", labelKey: "footer.link_rules" },
    ],
  },
  {
    icon: "👨‍💻",
    labelKey: "docs.developer",
    defaultOpen: false,
    items: [
      { href: "/docs#开发指南", labelKey: "docs.dev_guide" },
      { href: "/docs#claude-code", labelKey: "docs.claude_code" },
    ],
  },
  {
    icon: "💰",
    labelKey: "nav.pricing",
    defaultOpen: false,
    items: [
      { href: "/pricing", labelKey: "nav.pricing" },
    ],
  },
];

export default function DocsNav() {
  const { t } = useI18n();
  const pathname = usePathname();
  const [openSections, setOpenSections] = useState<Record<string, boolean>>(() => {
    const init: Record<string, boolean> = {};
    for (const s of navSections) {
      init[s.labelKey] = s.defaultOpen;
    }
    return init;
  });
  const [searchQuery, setSearchQuery] = useState("");
  const navRef = useRef<HTMLDivElement>(null);

  const toggleSection = (labelKey: string) => {
    setOpenSections((prev) => ({ ...prev, [labelKey]: !prev[labelKey] }));
  };

  const filteredSections = navSections
    .map((section) => ({
      ...section,
      label: t(section.labelKey),
      items: section.items
        .map((item) => ({ ...item, label: t(item.labelKey) }))
        .filter((item) => item.label.toLowerCase().includes(searchQuery.toLowerCase())),
    }))
    .filter((section) => section.items.length > 0);

  return (
    <aside
      ref={navRef}
      className="docs-sidebar"
    >
      {/* Search */}
      <div className="px-3 mb-4">
        <div className="relative">
          <svg
            className="absolute left-3 top-1/2 -translate-x-1/2 w-3.5 h-3.5 text-[var(--fg-muted)]"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            placeholder={t("nav.search") + "..."}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[var(--surface-raised)] border border-[var(--border)] rounded-lg pl-9 pr-8 py-2 text-xs text-[var(--fg)] placeholder:text-[var(--fg-muted)] focus:outline-none focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] transition-colors"
          />
          <kbd className="absolute right-2.5 top-1/2 -translate-x-1/2 text-[10px] text-[var(--fg-muted)] bg-[var(--surface)] px-1.5 py-0.5 rounded border border-[var(--border)] font-mono">
            ⌘K
          </kbd>
        </div>
      </div>

      {/* Navigation sections */}
      <nav className="px-3 space-y-0.5">
        {filteredSections.map((section) => {
          const isOpen = openSections[section.labelKey];
          return (
            <div key={section.labelKey} className="mb-1">
              <button
                onClick={() => toggleSection(section.labelKey)}
                className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium text-[var(--fg-dim)] hover:text-[var(--fg)] hover:bg-[var(--surface)] transition-colors"
              >
                <span className="flex-1 text-left">{section.label}</span>
                <svg
                  className={`w-3.5 h-3.5 transition-transform duration-200 ${
                    isOpen ? "rotate-180" : ""
                  }`}
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
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
