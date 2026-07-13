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
      <div className="relative bg-[var(--surface-raised)] border border-[var(--border)] rounded-2xl shadow-2xl w-[90vw] max-w-[560px] p-8 animate-[fadeInUp_0.3s_ease-out] max-h-[90vh] overflow-y-auto">
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

        {/* 更新内容 */}
        <div className="text-sm leading-relaxed space-y-3 mb-5">
          <p className="text-[var(--fg)]">{t("ann.modal.lead")}</p>
          <ul className="list-disc list-inside text-[var(--fg-dim)] space-y-1 ml-2">
            <li>{t("ann.modal.f1")}</li>
            <li>{t("ann.modal.f2")}</li>
            <li>{t("ann.modal.f3")}</li>
            <li>{t("ann.modal.f4")}</li>
            <li>{t("ann.modal.f5")}</li>
            <li>{t("ann.modal.f6")}</li>
            <li>{t("ann.modal.f7")}</li>
          </ul>
        </div>

        {/* 防骗声明 */}
        <div className="border-t border-[var(--border)] pt-4">
          <div className="flex items-center gap-2 mb-2">
            <span>⚠️</span>
            <h3 className="text-sm font-semibold text-[var(--fg)]">{t("ann.modal.notice_title")}</h3>
          </div>
          <p className="text-xs text-[var(--fg-dim)] mb-2">{t("notice.free")}</p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs border border-[var(--border)] rounded-lg overflow-hidden">
              <thead>
                <tr className="bg-[var(--surface)]">
                  <th className="text-left px-3 py-2 font-medium text-[var(--fg-dim)] border-b border-[var(--border)]">{t("notice.col_category")}</th>
                  <th className="text-left px-3 py-2 font-medium text-[var(--fg-dim)] border-b border-[var(--border)]">{t("notice.col_official")}</th>
                </tr>
              </thead>
              <tbody className="bg-[var(--bg)]">
                <tr className="border-b border-[var(--border)]">
                  <td className="px-3 py-2 text-[var(--fg-dim)]">{t("notice.label_website")}</td>
                  <td className="px-3 py-2"><a href="https://crazy-rest-reminder.pages.dev" target="_blank" rel="noopener noreferrer" className="text-[var(--accent)] hover:underline">crazy-rest-reminder.pages.dev</a></td>
                </tr>
                <tr className="border-b border-[var(--border)]">
                  <td className="px-3 py-2 text-[var(--fg-dim)]">{t("notice.label_source")}</td>
                  <td className="px-3 py-2"><a href="https://github.com/kuangketongxue/library-remind" target="_blank" rel="noopener noreferrer" className="text-[var(--accent)] hover:underline">github.com/kuangketongxue/library-remind</a></td>
                </tr>
                <tr className="border-b border-[var(--border)]">
                  <td className="px-3 py-2 text-[var(--fg-dim)]">{t("notice.label_download")}</td>
                  <td className="px-3 py-2"><a href="https://github.com/kuangketongxue/library-remind/releases/latest" target="_blank" rel="noopener noreferrer" className="text-[var(--accent)] hover:underline">GitHub Releases</a></td>
                </tr>
                <tr className="border-b border-[var(--border)]">
                  <td className="px-3 py-2 text-[var(--fg-dim)]">{t("notice.label_author")}</td>
                  <td className="px-3 py-2"><a href="https://github.com/kuangketongxue" target="_blank" rel="noopener noreferrer" className="text-[var(--accent)] hover:underline">@kuangketongxue</a></td>
                </tr>
                <tr>
                  <td className="px-3 py-2 text-[var(--fg-dim)]">{t("notice.label_report")}</td>
                  <td className="px-3 py-2"><a href="https://github.com/kuangketongxue/library-remind/issues" target="_blank" rel="noopener noreferrer" className="text-[var(--accent)] hover:underline">GitHub Issues</a></td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="text-xs text-[var(--fg-muted)] mt-2">
            {t("notice.scam")} <a href="https://github.com/kuangketongxue/library-remind/issues" target="_blank" rel="noopener noreferrer" className="text-[var(--accent)] hover:underline">{t("notice.scam_link")}</a> {t("notice.scam_suffix")}
          </p>
        </div>

        {/* 日期 + 按钮 */}
        <div className="flex items-center justify-between mt-5">
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
