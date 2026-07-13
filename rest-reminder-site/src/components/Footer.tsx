"use client";

import { useI18n } from "@/lib/i18n";

export default function Footer() {
  const { t } = useI18n();
  return (
    <footer className="bg-[var(--bg)] border-t border-[var(--border)]">
      {/* Hero CTA — WorkBuddy 风格 */}
      <div className="relative overflow-hidden">
        <div className="max-w-6xl mx-auto px-6 py-20 flex flex-col md:flex-row items-center gap-12">
          <div className="flex-1">
            <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-4 font-display text-[var(--fg)]">
              {t("footer.cta_title_1")}
              <br />
              <span className="text-[var(--accent)]">{t("footer.cta_title_2")}</span>
            </h2>
            <p className="text-base text-[var(--fg-dim)] leading-relaxed mb-8 max-w-lg">
              {t("footer.cta_desc")}
            </p>
            <a
              href="https://github.com/kuangketongxue/library-remind/releases/latest"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-[var(--accent)] text-white font-semibold px-8 py-3.5 rounded-lg text-sm hover:opacity-90 transition-opacity"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              {t("footer.cta_download")}
            </a>
          </div>
          <div className="flex-shrink-0 hidden md:block">
            <img src="/rest-reminder-logo.png" alt="Rest Reminder" className="w-40 h-40 rounded-2xl opacity-80" />
          </div>
        </div>
      </div>

      {/* 4-Column Footer — WorkBuddy 风格 */}
      <div className="border-t border-[var(--border)]">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-10">
            {/* 服务条款 */}
            <div>
              <h4 className="text-sm font-bold text-[var(--fg)] mb-4 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]"></span>
                {t("footer.col_terms")}
              </h4>
              <ul className="space-y-2.5">
                <li><a href="/terms" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">{t("footer.link_terms")}</a></li>
                <li><a href="/privacy" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">{t("footer.link_privacy")}</a></li>
                <li><a href="/rules" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">{t("footer.link_rules")}</a></li>
              </ul>
            </div>

            {/* 文档指引 */}
            <div>
              <h4 className="text-sm font-bold text-[var(--fg)] mb-4 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]"></span>
                {t("footer.col_docs")}
              </h4>
              <ul className="space-y-2.5">
                <li><a href="/docs" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">{t("footer.link_intro")}</a></li>
                <li><a href="/docs#常见问题" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">{t("footer.link_faq")}</a></li>
                <li><a href="https://github.com/kuangketongxue/library-remind/blob/main/CHANGELOG.md" target="_blank" rel="noopener noreferrer" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">{t("footer.link_changelog")}</a></li>
              </ul>
            </div>

            {/* 产品下载 */}
            <div>
              <h4 className="text-sm font-bold text-[var(--fg)] mb-4 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]"></span>
                {t("footer.col_download")}
              </h4>
              <ul className="space-y-2.5">
                <li><a href="https://github.com/kuangketongxue/library-remind/releases/latest" target="_blank" rel="noopener noreferrer" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">{t("footer.link_win_download")}</a></li>
                <li><a href="https://github.com/kuangketongxue/library-remind/releases" target="_blank" rel="noopener noreferrer" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">{t("footer.link_history")}</a></li>
                <li><a href="/pricing" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">{t("footer.link_pricing")}</a></li>
              </ul>
            </div>

            {/* 联系我们 */}
            <div>
              <h4 className="text-sm font-bold text-[var(--fg)] mb-4 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]"></span>
                {t("footer.col_contact")}
              </h4>
              <ul className="space-y-2.5">
                <li><a href="/contact" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">{t("footer.link_contact")}</a></li>
                <li><a href="https://github.com/kuangketongxue/library-remind/issues" target="_blank" rel="noopener noreferrer" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">{t("footer.link_issues")}</a></li>
                <li><a href="https://github.com/kuangketongxue/library-remind" target="_blank" rel="noopener noreferrer" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">{t("footer.link_github")}</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-[var(--border)]">
        <div className="max-w-6xl mx-auto px-6 py-5 flex flex-col md:flex-row justify-between items-center gap-3">
          <p className="text-xs text-[var(--fg-muted)]">
            {t("footer.copyright")}
          </p>
          <p className="text-xs text-[var(--fg-muted)]">
            {t("footer.made_by")}
          </p>
        </div>
      </div>
    </footer>
  );
}
