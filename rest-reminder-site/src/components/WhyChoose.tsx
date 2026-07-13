"use client";

import { useI18n } from "@/lib/i18n";

const reasons = [
  {
    icon: "⏱️",
    titleKey: "hero.whychoose.r1.title",
    descKey: "hero.whychoose.r1.desc",
  },
  {
    icon: "👁️",
    titleKey: "hero.whychoose.r2.title",
    descKey: "hero.whychoose.r2.desc",
  },
  {
    icon: "🎬",
    titleKey: "hero.whychoose.r3.title",
    descKey: "hero.whychoose.r3.desc",
  },
  {
    icon: "📊",
    titleKey: "hero.whychoose.r4.title",
    descKey: "hero.whychoose.r4.desc",
  },
  {
    icon: "🤖",
    titleKey: "hero.whychoose.r5.title",
    descKey: "hero.whychoose.r5.desc",
  },
  {
    icon: "🪶",
    titleKey: "hero.whychoose.r6.title",
    descKey: "hero.whychoose.r6.desc",
  },
];

export default function WhyChoose() {
  const { t } = useI18n();
  return (
    <section className="py-20 px-6 section-glow">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl md:text-[2.5rem] font-extrabold tracking-tight mb-3 font-display">{t("hero.whychoose.title")}</h2>
        <p className="text-[var(--fg-dim)] text-lg mb-10">{t("hero.whychoose.subtitle")}</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reasons.map((r) => (
            <div key={r.titleKey} className="border border-[var(--border)] rounded-xl p-6 bg-[var(--surface)] hover:border-[var(--accent)] hover:bg-[var(--surface-hover)] transition-colors">
              <div className="text-2xl mb-3">{r.icon}</div>
              <h3 className="text-[15px] font-semibold mb-1.5 tracking-tight">{t(r.titleKey)}</h3>
              <p className="text-[13px] text-[var(--fg-dim)] leading-relaxed">{t(r.descKey)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
