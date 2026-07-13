"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { useI18n } from "@/lib/i18n";

export default function AnnouncementModal() {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    // 只在首页弹出
    if (pathname !== "/") return;
    const timer = setTimeout(() => setOpen(true), 800);
    return () => clearTimeout(timer);
  }, [pathname]);

  const dismiss = () => {
    setOpen(false);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center">
      {/* 遮罩 */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={dismiss}
      />
      {/* 弹窗 */}
      <div className="relative bg-[var(--surface-raised)] border border-[var(--border)] rounded-2xl shadow-2xl w-[90vw] max-w-[520px] p-8 animate-[fadeInUp_0.3s_ease-out]">
        {/* 关闭按钮 */}
        <button
          onClick={dismiss}
          className="absolute top-4 right-4 text-[var(--fg-muted)] hover:text-[var(--fg)] transition-colors text-xl leading-none"
          aria-label={t("ann.modal.close")}
        >
          ✕
        </button>

        {/* 标题 */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-xl">📢</span>
          <h2 className="text-lg font-bold text-[var(--fg)]">{t("ann.modal.title")}</h2>
        </div>

        {/* 内容 */}
        <div className="text-sm leading-relaxed space-y-4 mb-6">
          <p className="text-[var(--fg-dim)]">
            {t("ann.modal.intro")}
          </p>

          <div>
            <p className="font-semibold text-[var(--fg)] mb-1">{t("ann.modal.s1.title")}</p>
            <ul className="list-disc list-inside text-[var(--fg-dim)] space-y-0.5 ml-2">
              <li>{t("ann.modal.s1.i1")}</li>
              <li>{t("ann.modal.s1.i2")}</li>
            </ul>
          </div>

          <div>
            <p className="font-semibold text-[var(--fg)] mb-1">{t("ann.modal.s2.title")}</p>
            <ul className="list-disc list-inside text-[var(--fg-dim)] space-y-0.5 ml-2">
              <li>{t("ann.modal.s2.i1")}</li>
              <li>{t("ann.modal.s2.i2")}</li>
            </ul>
          </div>

          <div>
            <p className="font-semibold text-[var(--fg)] mb-1">{t("ann.modal.s3.title")}</p>
            <ul className="list-disc list-inside text-[var(--fg-dim)] space-y-0.5 ml-2">
              <li>{t("ann.modal.s3.i1")}</li>
              <li>{t("ann.modal.s3.i2")}</li>
            </ul>
          </div>
        </div>

        {/* 日期 + 按钮 */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-[var(--fg-muted)]">{t("ann.modal.date")}</span>
          <button
            onClick={dismiss}
            className="px-6 py-2 text-sm font-medium rounded-lg border border-[var(--accent)] text-[var(--accent)] hover:bg-[var(--accent-soft)] transition-colors"
          >
            {t("ann.modal.dismiss")}
          </button>
        </div>
      </div>
    </div>
  );
}
