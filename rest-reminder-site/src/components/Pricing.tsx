"use client";

import { useI18n } from "@/lib/i18n";
import { SectionHeader, ScaleIn } from "./Animations";

const features = [
  { textKey: "hero.pricing.feature1", included: true },
  { textKey: "hero.pricing.feature2", included: true },
  { textKey: "hero.pricing.feature3", included: true },
  { textKey: "hero.pricing.feature4", included: true },
  { textKey: "hero.pricing.feature5", included: true },
  { textKey: "hero.pricing.feature6", included: true, highlight: true },
  { textKey: "hero.pricing.feature7", included: true },
];

export default function Pricing() {
  const { t } = useI18n();
  return (
    <section className="py-28 px-6 section-glow" id="pricing">
      <div className="max-w-6xl mx-auto">
        <SectionHeader label={t("hero.pricing.label")} title={t("hero.pricing.title")} subtitle={t("hero.pricing.subtitle")} />

        <div className="max-w-2xl mx-auto">
          <ScaleIn>
            <div className="card p-9 text-center">
              <h3 className="text-3xl font-bold font-display mb-2">{t("hero.pricing.price_label")}</h3>
              <p className="text-sm text-[var(--fg-dim)] mb-8">{t("hero.pricing.price_desc")}</p>

              <ul className="space-y-3.5 mb-8 text-left max-w-sm mx-auto">
                {features.map((f) => (
                  <li key={f.textKey} className="flex items-start gap-3 text-sm text-[var(--fg-dim)]">
                    <span className={`mt-0.5 text-[var(--accent)] ${f.highlight ? 'font-bold' : ''}`}>
                      {f.included ? '✓' : '✗'}
                    </span>
                    <span className={f.highlight ? 'font-semibold text-[var(--fg)]' : ''}>{t(f.textKey)}</span>
                  </li>
                ))}
              </ul>

              <a
                href="#download"
                className="inline-block py-3.5 px-8 text-sm font-semibold btn-primary btn-shine"
              >
                {t("hero.pricing.cta")}
              </a>
            </div>
          </ScaleIn>
        </div>
      </div>
    </section>
  );
}
