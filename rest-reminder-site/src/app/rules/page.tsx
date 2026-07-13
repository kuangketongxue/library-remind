"use client";

import DocsNav from "@/components/DocsNav";
import { useI18n } from "@/lib/i18n";

export default function RulesPage() {
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
            <span className="text-[var(--fg)]">{t("rules.title")}</span>
          </nav>

          <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">{t("rules.title")}</h1>
          <p className="text-[var(--fg-dim)] mb-10">{t("rules.subtitle")}</p>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("rules.section_behavior")}</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("rules.behavior.respect")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("rules.behavior.respect_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("rules.behavior.focus")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("rules.behavior.focus_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("rules.behavior.collaborate")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("rules.behavior.collaborate_desc")}
                </p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("rules.section_issue")}</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("rules.issue.check")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">{t("rules.issue.check_desc")}</p>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li>{t("rules.issue.check_0")}</li>
                  <li>{t("rules.issue.check_1")}</li>
                  <li>{t("rules.issue.check_2")}</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("rules.issue.bug")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">{t("rules.issue.bug_desc")}</p>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li><strong>{t("rules.issue.bug_0_label")}</strong> — {t("rules.issue.bug_0")}</li>
                  <li><strong>{t("rules.issue.bug_1_label")}</strong> — {t("rules.issue.bug_1")}</li>
                  <li><strong>{t("rules.issue.bug_2_label")}</strong> — {t("rules.issue.bug_2")}</li>
                  <li><strong>{t("rules.issue.bug_3_label")}</strong> — {t("rules.issue.bug_3")}</li>
                  <li><strong>{t("rules.issue.bug_4_label")}</strong> — {t("rules.issue.bug_4")}</li>
                  <li><strong>{t("rules.issue.bug_5_label")}</strong> — {t("rules.issue.bug_5")}</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("rules.issue.feature")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("rules.issue.feature_desc")}
                </p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("rules.section_pr")}</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("rules.pr.before")}</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li>{t("rules.pr.before_0")}</li>
                  <li>{t("rules.pr.before_1")}</li>
                  <li>{t("rules.pr.before_2")}</li>
                  <li>{t("rules.pr.before_3")}</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("rules.pr.desc")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">{t("rules.pr.desc_desc")}</p>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li>{t("rules.pr.desc_0")}</li>
                  <li>{t("rules.pr.desc_1")}</li>
                  <li>{t("rules.pr.desc_2")}</li>
                  <li>{t("rules.pr.desc_3")}</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("rules.pr.review")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("rules.pr.review_desc")}
                </p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("rules.section_violation")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                {t("rules.violation_desc")}
              </p>
            </div>
          </section>

          <section className="mb-16">
            <h2 className="text-xl font-bold mb-4 font-display">{t("rules.section_versioning")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">{t("rules.versioning_desc")}</p>
              <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                <li><strong>{t("rules.versioning_0_label")}</strong> — {t("rules.versioning_0")}</li>
                <li><strong>{t("rules.versioning_1_label")}</strong> — {t("rules.versioning_1")}</li>
                <li><strong>{t("rules.versioning_2_label")}</strong> — {t("rules.versioning_2")}</li>
              </ul>
            </div>
          </section>

          <nav className="border-t border-[var(--border)] pt-8 mt-16 flex flex-col sm:flex-row justify-between gap-4">
            <a href="/terms" className="group flex items-center gap-3 text-sm">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <div>
                <p className="text-[var(--fg-muted)] text-xs">{t("nav.prev_page")}</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">{t("footer.link_terms")}</p>
              </div>
            </a>
            <a href="/pricing" className="group flex items-center gap-3 text-sm sm:flex-row-reverse">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <div className="sm:text-right">
                <p className="text-[var(--fg-muted)] text-xs">{t("nav.next_page")}</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">{t("nav.pricing")}</p>
              </div>
            </a>
          </nav>
        </div>
      </div>
    </main>
  );
}
