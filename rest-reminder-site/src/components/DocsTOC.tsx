"use client";

import { useState, useEffect } from "react";

const tocItems = [
  { id: "快速开始", label: "快速开始" },
  { id: "下载运行", label: "下载运行" },
  { id: "设定目标", label: "设定目标" },
  { id: "开始学习", label: "开始学习" },
  { id: "复盘追踪", label: "复盘追踪" },
  { id: "专注循环", label: "60 分钟专注循环" },
  { id: "护眼提醒", label: "20-20-20 护眼提醒" },
  { id: "学习追踪", label: "学习时长追踪" },
  { id: "趋势分析", label: "趋势分析" },
  { id: "ai分析", label: "AI 学习分析" },
  { id: "设置详解", label: "设置详解" },
  { id: "更新日志", label: "更新日志" },
  { id: "常见问题", label: "常见问题" },
];

export default function DocsTOC() {
  const [active, setActive] = useState("");

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) setActive(entry.target.id);
        }
      },
      { rootMargin: "-80px 0px -70% 0px" }
    );
    tocItems.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  return (
    <aside className="docs-toc hidden lg:block">
      <p className="text-xs font-bold text-[var(--fg)] mb-4 tracking-wide uppercase">快速导航</p>
      <nav className="space-y-1">
        {tocItems.map(({ id, label }) => (
          <a
            key={id}
            href={`#${id}`}
            className={`block text-[13px] py-1 transition-colors border-l-2 pl-3 ${
              active === id
                ? "text-[var(--accent)] font-medium border-[var(--accent)]"
                : "text-[var(--fg-dim)] hover:text-[var(--fg)] border-transparent"
            }`}
          >
            {label}
          </a>
        ))}
      </nav>
    </aside>
  );
}
