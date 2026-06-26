"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/docs", label: "快速开始" },
  { href: "/docs#功能说明", label: "功能说明" },
  { href: "/docs#更新日志", label: "更新日志" },
  { href: "/docs#常见问题", label: "常见问题" },
];

export default function DocsNav() {
  const pathname = usePathname();

  return (
    <aside className="w-56 shrink-0 sticky top-20 h-[calc(100vh-5rem)] overflow-y-auto py-8 hidden lg:block">
      <nav className="space-y-1">
        <p className="text-xs font-semibold text-[var(--fg-dim)] uppercase tracking-wider mb-3 px-3">文档</p>
        {navItems.map((item) => (
          <a
            key={item.href}
            href={item.href}
            className={`block text-sm px-3 py-1.5 rounded-lg transition-colors ${
              pathname === item.href.split("#")[0]
                ? "text-[var(--accent)] bg-[var(--accent-soft)]"
                : "text-[var(--fg-dim)] hover:text-[var(--fg)] hover:bg-[var(--surface)]"
            }`}
          >
            {item.label}
          </a>
        ))}
      </nav>
    </aside>
  );
}
