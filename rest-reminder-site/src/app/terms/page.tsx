"use client";

import DocsNav from "@/components/DocsNav";
import { useI18n } from "@/lib/i18n";

export default function TermsPage() {
  const { t } = useI18n();
  return (
    <main className="flex-1">
      <div className="docs-layout">
        <DocsNav />
        <div className="docs-main" style={{ maxWidth: "960px" }}>
          <nav className="flex items-center gap-2 text-xs text-[var(--fg-dim)] mb-6">
            <a href="/" className="hover:text-[var(--fg)] transition-colors">{t("nav.docs")}</a>
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-[var(--fg)]">{t("terms.title")}</span>
          </nav>

          <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">{t("terms.title")}</h1>
          <p className="text-[var(--fg-dim)] mb-10">{t("terms.subtitle")}</p>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("terms.section_license")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                {t("terms.license_desc_1")}<strong>{t("terms.license_mit")}</strong>{t("terms.license_desc_2")}
              </p>
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                {t("terms.license_desc_3")}
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("terms.section_disclaimer")}</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("terms.disclaimer_as_is_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("terms.disclaimer_as_is_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("terms.disclaimer_health_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("terms.disclaimer_health_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("terms.disclaimer_results_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("terms.disclaimer_results_desc")}
                </p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("terms.section_limits")}</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("terms.limits_platform_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("terms.limits_platform_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("terms.limits_python_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("terms.limits_python_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("terms.limits_ai_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("terms.limits_ai_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("terms.limits_banned_title")}</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li>{t("terms.limits_banned_1")}</li>
                  <li>{t("terms.limits_banned_2")}</li>
                  <li>{t("terms.limits_banned_3")}</li>
                  <li>{t("terms.limits_banned_4")}</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("terms.section_changes")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                {t("terms.changes_desc")}
              </p>
            </div>
          </section>

          <section className="mb-16">
            <h2 className="text-xl font-bold mb-4 font-display">{t("terms.section_contact")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                {t("terms.contact_desc")} <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">{t("terms.contact_email")}</code>{t("terms.contact_period")}
              </p>
            </div>
          </section>

          <nav className="border-t border-[var(--border)] pt-8 mt-16 flex flex-col sm:flex-row justify-between gap-4">
            <a href="/privacy" className="group flex items-center gap-3 text-sm">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <div>
                <p className="text-[var(--fg-muted)] text-xs">{t("nav.prev_page")}</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">{t("nav.privacy")}</p>
              </div>
            </a>
            <a href="/rules" className="group flex items-center gap-3 text-sm sm:flex-row-reverse">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <div className="sm:text-right">
                <p className="text-[var(--fg-muted)] text-xs">{t("nav.next_page")}</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">{t("nav.rules")}</p>
              </div>
            </a>
          </nav>
        </div>
      </div>
    </main>
  );
}
