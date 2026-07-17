"use client";

import DocsNav from "@/components/DocsNav";
import { useI18n } from "@/lib/i18n";

export default function PricingPage() {
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
            <span className="text-[var(--fg)]">{t("nav.pricing")}</span>
          </nav>

          <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">{t("pricing.title")}</h1>
          <p className="text-[var(--fg-dim)] mb-10">{t("pricing.subtitle")}</p>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("pricing.section_core")}</h2>
            <div className="docs-card" style={{ borderLeft: "3px solid var(--accent)" }}>
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                {t("pricing.core_desc")}
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("pricing.section_features")}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("pricing.card_core_title")}</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1.5">
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_core.0")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_core.1")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_core.2")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_core.3")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_core.4")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_core.5")}</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("pricing.card_tracking_title")}</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1.5">
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_tracking.0")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_tracking.1")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_tracking.2")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_tracking.3")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_tracking.4")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_tracking.5")}</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("pricing.card_ai_title")}</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1.5">
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_ai.0")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_ai.1")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_ai.2")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_ai.3")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_ai.4")}</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("pricing.card_integrations_title")}</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1.5">
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_integrations.0")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_integrations.1")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_integrations.2")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_integrations.3")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_integrations.4")}</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> {t("pricing.card_integrations.5")}</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("pricing.section_plans")}</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("pricing.plan_name")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  <strong>{t("pricing.plan_desc")}</strong>
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("pricing.ai_costs")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("pricing.ai_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("pricing.no_hidden")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("pricing.no_hidden_desc")}
                </p>
              </div>
            </div>
          </section>

          <section className="mb-16">
            <h2 className="text-xl font-bold mb-4 font-display">{t("pricing.section_faq")}</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("pricing.faq_why")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("pricing.faq_why_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("pricing.faq_will")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("pricing.faq_will_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("pricing.faq_support")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("pricing.faq_support_desc")}
                </p>
              </div>
            </div>
          </section>

          <nav className="border-t border-[var(--border)] pt-8 mt-16 flex flex-col sm:flex-row justify-between gap-4">
            <a href="/rules" className="group flex items-center gap-3 text-sm">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <div>
                <p className="text-[var(--fg-muted)] text-xs">{t("nav.prev_page")}</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">{t("nav.rules")}</p>
              </div>
            </a>
            <a href="/docs" className="group flex items-center gap-3 text-sm sm:flex-row-reverse">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <div className="sm:text-right">
                <p className="text-[var(--fg-muted)] text-xs">{t("nav.next_page")}</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">{t("nav.docs")}</p>
              </div>
            </a>
          </nav>
        </div>
      </div>
    </main>
  );
}
