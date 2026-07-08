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
            <a href="/" className="hover:text-[var(--fg)] transition-colors">{t("nav.docs")}</a>
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
                <h3 className="text-sm font-semibold mb-2">Core</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1.5">
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 60-min focus cycle</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 5-min mindfulness countdown</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 5-min break</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Auto-open Bilibili favorites</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 20-20-20 eye care</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Eye-care video every 3 rounds</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">Tracking</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1.5">
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Study time tracking</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Review scoring</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Streaks + milestones</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Trends (weekly/monthly/quarterly/yearly)</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 7x24 heatmap</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 17 achievements</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">AI</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1.5">
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> AI learning reports</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Daily / weekly / monthly / quarterly / yearly</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Multi-provider switching</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Local fallback without API key</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> TTS voice broadcast</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">Integrations</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1.5">
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Feishu Calendar</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Ambient noise</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Theme switching</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Global shortcuts</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> Battery monitor</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> GitHub backup</li>
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
                <p className="text-[var(--fg-muted)] text-xs">Previous</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">Community Rules</p>
              </div>
            </a>
            <a href="/docs" className="group flex items-center gap-3 text-sm sm:flex-row-reverse">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <div className="sm:text-right">
                <p className="text-[var(--fg-muted)] text-xs">Next</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">Documentation</p>
              </div>
            </a>
          </nav>
        </div>
      </div>
    </main>
  );
}
