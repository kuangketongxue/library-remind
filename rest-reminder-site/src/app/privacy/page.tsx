"use client";

import DocsNav from "@/components/DocsNav";
import { useI18n } from "@/lib/i18n";

export default function PrivacyPage() {
  const { t } = useI18n();
  return (
    <main className="flex-1">
      <div className="docs-layout">
        <DocsNav />
        <div className="docs-main" style={{ maxWidth: "960px" }}>
          <nav className="flex items-center gap-2 text-xs text-[var(--fg-dim)] mb-6">
            <a href="/" className="hover:text-[var(--fg)] transition-colors">Rest Reminder</a>
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-[var(--fg)]">{t("privacy.title")}</span>
          </nav>

          <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">{t("privacy.title")}</h1>
          <p className="text-[var(--fg-dim)] mb-10">{t("privacy.subtitle")}</p>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("privacy.section_storage")}</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("privacy.storage_local_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("privacy.storage_local_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("privacy.storage_no_account_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("privacy.storage_no_account_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("privacy.storage_no_upload_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("privacy.storage_no_upload_desc")}
                </p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("privacy.section_files")}</h2>
            <div className="space-y-3">
              <div className="flex gap-3">
                <code className="bg-[var(--surface)] px-2 py-1 rounded text-xs font-mono text-[var(--accent)] shrink-0">.daily_log.json</code>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("privacy.files_daily")}</p>
              </div>
              <div className="flex gap-3">
                <code className="bg-[var(--surface)] px-2 py-1 rounded text-xs font-mono text-[var(--accent)] shrink-0">.review_log.json</code>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("privacy.files_review")}</p>
              </div>
              <div className="flex gap-3">
                <code className="bg-[var(--surface)] px-2 py-1 rounded text-xs font-mono text-[var(--accent)] shrink-0">.streak.json</code>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("privacy.files_streak")}</p>
              </div>
              <div className="flex gap-3">
                <code className="bg-[var(--surface)] px-2 py-1 rounded text-xs font-mono text-[var(--accent)] shrink-0">.settings.json</code>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("privacy.files_settings")}</p>
              </div>
              <div className="flex gap-3">
                <code className="bg-[var(--surface)] px-2 py-1 rounded text-xs font-mono text-[var(--accent)] shrink-0">.app_state.json</code>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("privacy.files_state")}</p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("privacy.section_audit")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                {t("privacy.audit_desc")}
              </p>
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                {t("privacy.audit_repo")}<a href="https://github.com/kuangketongxue/library-remind" target="_blank" rel="noopener noreferrer" className="text-[var(--accent)] hover:underline">github.com/kuangketongxue/library-remind</a>
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("privacy.section_ai")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                {t("privacy.ai_desc")}
              </p>
              <ul className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3 space-y-1 list-disc list-inside">
                <li>{t("privacy.ai_item_time")}</li>
                <li>{t("privacy.ai_item_score")}</li>
                <li>{t("privacy.ai_item_streak")}</li>
              </ul>
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                {t("privacy.ai_no_pii")}
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("privacy.section_third")}</h2>
            <div className="space-y-3">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("privacy.third_bili_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("privacy.third_bili_desc")}
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("privacy.third_lark_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("privacy.third_lark_desc")}
                </p>
              </div>
            </div>
          </section>

          <section className="mb-16">
            <h2 className="text-xl font-bold mb-4 font-display">{t("privacy.section_delete")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                {t("privacy.delete_desc")}
              </p>
            </div>
          </section>

          <nav className="border-t border-[var(--border)] pt-8 mt-16 flex flex-col sm:flex-row justify-between gap-4">
            <a href="/docs" className="group flex items-center gap-3 text-sm">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <div>
                <p className="text-[var(--fg-muted)] text-xs">{t("nav.prev_page")}</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">{t("nav.docs")}</p>
              </div>
            </a>
            <a href="/terms" className="group flex items-center gap-3 text-sm sm:flex-row-reverse">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <div className="sm:text-right">
                <p className="text-[var(--fg-muted)] text-xs">{t("nav.next_page")}</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">{t("nav.terms")}</p>
              </div>
            </a>
          </nav>
        </div>
      </div>
    </main>
  );
}
