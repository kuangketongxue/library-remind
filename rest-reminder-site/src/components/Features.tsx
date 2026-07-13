"use client";

import { useI18n } from "@/lib/i18n";

const features = [
  {
    icon: "⏱️",
    titleKey: "hero.features.focus.title",
    descKey: "hero.features.focus.desc",
  },
  {
    icon: "👁️",
    titleKey: "hero.features.eye.title",
    descKey: "hero.features.eye.desc",
  },
  {
    icon: "📊",
    titleKey: "hero.features.track.title",
    descKey: "hero.features.track.desc",
  },
  {
    icon: "📈",
    titleKey: "hero.features.trends.title",
    descKey: "hero.features.trends.desc",
  },
  {
    icon: "🤖",
    titleKey: "hero.features.ai.title",
    descKey: "hero.features.ai.desc",
  },
  {
    icon: "🔒",
    titleKey: "hero.features.offline.title",
    descKey: "hero.features.offline.desc",
  },
];

const rows = [
  { featureKey: "hero.features.comparison.row1.feature", rr: "✓", fq: "✗", xt: "✗" },
  { featureKey: "hero.features.comparison.row2.feature", rr: "✓", fq: "✗", xt: "✗" },
  { featureKey: "hero.features.comparison.row3.feature", rrKey: "hero.features.comparison.row3.rr", fq: "✗", xt: "✗" },
  { featureKey: "hero.features.comparison.row4.feature", rrKey: "hero.features.comparison.row4.rr", fq: "✗", xt: "✗" },
  { featureKey: "hero.features.comparison.row5.feature", rr: "✓", fq: "✗", xt: "✗" },
  { featureKey: "hero.features.comparison.row6.feature", rr: "✓", fq: "✗", xt: "✗" },
  { featureKey: "hero.features.comparison.row7.feature", rr: "✓", fq: "✗", xt: "✓" },
  { featureKey: "hero.features.comparison.row8.feature", rr: "✓", fq: "✗", xt: "✗" },
  { featureKey: "hero.features.comparison.row9.feature", rr: "✓", fqKey: "hero.features.comparison.row9.fq", xt: "✗" },
];

export default function Features() {
  const { t } = useI18n();
  return (
    <section className="py-24 px-6" id="features">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl md:text-[2.5rem] font-extrabold tracking-tight mb-3 font-display">{t("hero.features.title")}</h2>
        <p className="text-[var(--fg-dim)] text-lg mb-14">{t("hero.features.subtitle")}</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((f) => (
            <div key={f.titleKey} className="card p-7 group">
              <div className="text-3xl mb-4 group-hover:scale-110 transition-transform duration-300">{f.icon}</div>
              <h3 className="text-[15px] font-semibold mb-2 tracking-tight">{t(f.titleKey)}</h3>
              <p className="text-[13px] text-[var(--fg-dim)] leading-relaxed">{t(f.descKey)}</p>
            </div>
          ))}
        </div>

        {/* Comparison table */}
        <div className="mt-20">
          <h3 className="text-xl font-bold mb-6 font-display">{t("hero.features.comparison.title")}</h3>
          <div className="border border-[var(--border)] overflow-hidden rounded-2xl">
            <div className="grid grid-cols-4 text-[11px] border-b border-[var(--border)]">
              <div className="p-4 text-[var(--fg-dim)] font-semibold tracking-wider uppercase">{t("hero.features.comparison.col_feature")}</div>
              <div className="p-4 text-center font-semibold text-[var(--accent)] bg-[var(--accent-soft)]">{t("hero.features.comparison.col_rr")}</div>
              <div className="p-4 text-center text-[var(--fg-dim)]">{t("hero.features.comparison.col_fq")}</div>
              <div className="p-4 text-center text-[var(--fg-dim)]">{t("hero.features.comparison.col_xt")}</div>
            </div>
            {rows.map((r, i) => (
              <div key={i} className="grid grid-cols-4 text-[13px] border-b border-[var(--border)] last:border-b-0 hover:bg-[var(--surface-hover)] transition-colors">
                <div className="p-4 text-[var(--fg-dim)]">{t(r.featureKey)}</div>
                <div className="p-4 text-center text-[var(--accent)] font-medium bg-[var(--accent-soft)]">{r.rrKey ? t(r.rrKey) : r.rr}</div>
                <div className="p-4 text-center text-[var(--fg-dim)]">{r.fqKey ? t(r.fqKey) : r.fq}</div>
                <div className="p-4 text-center text-[var(--fg-dim)]">{r.xt}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
