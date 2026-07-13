"use client";

import { useState, useEffect } from "react";
import { useI18n } from "@/lib/i18n";

const tocItems = [
  { id: "简介", labelKey: "docs.section_intro" },
  { id: "快速开始", labelKey: "docs.section_quickstart" },
  { id: "下载运行", labelKey: "docs.download_run" },
  { id: "设定目标", labelKey: "docs.set_goal" },
  { id: "开始学习", labelKey: "docs.start_learn" },
  { id: "复盘追踪", labelKey: "docs.review_track" },
  { id: "专注循环", labelKey: "docs.focus_cycle" },
  { id: "护眼提醒", labelKey: "docs.eye_care" },
  { id: "学习追踪", labelKey: "docs.learning_track" },
  { id: "趋势分析", labelKey: "docs.trends" },
  { id: "ai分析", labelKey: "docs.ai_analysis" },
  { id: "设置详解", labelKey: "docs.settings" },
  { id: "更新日志", labelKey: "docs.changelog" },
  { id: "常见问题", labelKey: "docs.faq" },
];

export default function DocsTOC() {
  const { t } = useI18n();
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
      <p className="text-xs font-bold text-[var(--fg)] mb-4 tracking-wide uppercase">{t("docs.toc_title")}</p>
      <nav className="space-y-1">
        {tocItems.map(({ id, labelKey }) => (
          <a
            key={id}
            href={`#${id}`}
            className={`block text-[13px] py-1 transition-colors border-l-2 pl-3 ${
              active === id
                ? "text-[var(--accent)] font-medium border-[var(--accent)]"
                : "text-[var(--fg-dim)] hover:text-[var(--fg)] border-transparent"
            }`}
          >
            {t(labelKey)}
          </a>
        ))}
      </nav>
    </aside>
  );
}
