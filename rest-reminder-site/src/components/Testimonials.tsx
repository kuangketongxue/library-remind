"use client";

import { useI18n } from "@/lib/i18n";

const testimonials = [
  {
    nameKey: "hero.testimonials.t1.name",
    roleKey: "hero.testimonials.t1.role",
    textKey: "hero.testimonials.t1.text",
    stars: 5,
  },
  {
    nameKey: "hero.testimonials.t2.name",
    roleKey: "hero.testimonials.t2.role",
    textKey: "hero.testimonials.t2.text",
    stars: 5,
  },
  {
    nameKey: "hero.testimonials.t3.name",
    roleKey: "hero.testimonials.t3.role",
    textKey: "hero.testimonials.t3.text",
    stars: 5,
  },
];

export default function Testimonials() {
  const { t } = useI18n();
  return (
    <section className="py-20 px-6 section-glow">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-center mb-3 font-display">{t("hero.testimonials.title")}</h2>
        <p className="text-[var(--fg-dim)] text-center text-lg mb-10">{t("hero.testimonials.subtitle")}</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {testimonials.map((item) => (
            <div key={item.nameKey} className="border border-[var(--border)] rounded-xl p-6 bg-[var(--surface)] hover:border-[var(--accent)] hover:bg-[var(--surface-hover)] transition-colors">
              <div className="flex gap-0.5 mb-3">
                {Array.from({ length: item.stars }).map((_, i) => (
                  <span key={i} className="text-[var(--accent)] text-xs">&#9733;</span>
                ))}
              </div>
              <p className="text-[13px] text-[var(--fg-dim)] leading-relaxed mb-4">
                &ldquo;{t(item.textKey)}&rdquo;
              </p>
              <div className="flex items-center gap-2.5 pt-3 border-t border-[var(--border)]">
                <div className="w-7 h-7 rounded-sm bg-[var(--surface-hover)] border border-[var(--border)] flex items-center justify-center text-[11px] text-[var(--fg-dim)] font-mono">
                  {t(item.nameKey)[0]}
                </div>
                <div>
                  <div className="font-medium text-[13px]">{t(item.nameKey)}</div>
                  <div className="text-[11px] text-[var(--fg-dim)]">{t(item.roleKey)}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
