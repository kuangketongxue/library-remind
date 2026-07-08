"use client";

import { useI18n } from "@/lib/i18n";

export default function OfficialNotice() {
  const { t } = useI18n();
  return (
    <div className="bg-[rgba(212,175,55,0.08)] border-b border-[rgba(212,175,55,0.2)]">
      <div className="max-w-6xl mx-auto px-6 py-3">
        <div className="flex items-start gap-3">
          <span className="text-base mt-0.5">⚠️</span>
          <div className="flex-1">
            <p className="text-sm font-semibold text-[var(--fg)] mb-1.5">{t("notice.warning")}</p>
            <p className="text-xs text-[var(--fg-dim)] mb-2">{t("notice.free")}</p>
            <div className="overflow-x-auto">
              <table className="w-full text-xs border border-[var(--border)] rounded-lg overflow-hidden">
                <thead>
                  <tr className="bg-[var(--surface)]">
                    <th className="text-left px-3 py-2 font-medium text-[var(--fg-dim)] border-b border-[var(--border)]">类别</th>
                    <th className="text-left px-3 py-2 font-medium text-[var(--fg-dim)] border-b border-[var(--border)]">唯一官方</th>
                  </tr>
                </thead>
                <tbody className="bg-[var(--bg)]">
                  <tr className="border-b border-[var(--border)]">
                    <td className="px-3 py-2 text-[var(--fg-dim)]">{t("notice.label_website")}</td>
                    <td className="px-3 py-2"><a href="https://crazy-rest-reminder.pages.dev" className="text-[var(--accent)] hover:underline">crazy-rest-reminder.pages.dev</a></td>
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
        </div>
      </div>
    </div>
  );
}
