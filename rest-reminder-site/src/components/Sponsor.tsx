"use client";

import { useI18n } from "@/lib/i18n";
import { motion } from "framer-motion";

const fade = (delay = 0) => ({
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] as const },
});

const sponsors = [
  { nameKey: "hero.sponsor.s1.name", descKey: "hero.sponsor.s1.desc", url: "https://ccswitch.io" },
  { nameKey: "hero.sponsor.s2.name", descKey: "hero.sponsor.s2.desc", url: "https://kimi.moonshot.cn" },
];

const techSupport = [
  { nameKey: "hero.sponsor.p1.name", descKey: "hero.sponsor.p1.desc" },
  { nameKey: "hero.sponsor.p2.name", descKey: "hero.sponsor.p2.desc" },
  { nameKey: "hero.sponsor.p3.name", descKey: "hero.sponsor.p3.desc" },
];

export default function Sponsor() {
  const { t } = useI18n();
  return (
    <section className="py-24 px-6" id="sponsor">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div {...fade(0)} className="text-center mb-16">
          <p className="text-[var(--accent)] text-sm font-medium mb-4 tracking-wide">{t("hero.sponsor.ecosystem")}</p>
          <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-5 font-display">
            {t("hero.sponsor.title")}
          </h2>
          <p className="text-[var(--fg-dim)] text-lg max-w-2xl mx-auto leading-relaxed">
            {t("hero.sponsor.subtitle")}
          </p>
        </motion.div>

        {/* Sponsors */}
        <motion.div {...fade(0.1)} className="text-center mb-16">
          <h3 className="text-2xl md:text-3xl font-bold mb-3 font-display">{t("hero.sponsor.sponsors_title")}</h3>
          <p className="text-[var(--fg-dim)] mb-10">{t("hero.sponsor.sponsors_subtitle")}</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
            {sponsors.map((s) => (
              <a key={s.nameKey} href={s.url} target="_blank" rel="noopener noreferrer" className="card p-6 text-left group">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-[var(--surface-raised)] flex items-center justify-center text-xl font-bold text-[var(--accent)] group-hover:bg-[var(--accent-soft)] transition-colors">
                    {t(s.nameKey)[0]}
                  </div>
                  <h4 className="text-sm font-bold">{t(s.nameKey)}</h4>
                </div>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t(s.descKey)}</p>
              </a>
            ))}
          </div>
        </motion.div>

        {/* Technical partners */}
        <motion.div {...fade(0.15)} className="text-center mb-16">
          <h3 className="text-2xl md:text-3xl font-bold mb-3 font-display">{t("hero.sponsor.partners_title")}</h3>
          <p className="text-[var(--fg-dim)] mb-10">{t("hero.sponsor.partners_subtitle")}</p>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 max-w-3xl mx-auto">
            {techSupport.map((s) => (
              <div key={s.nameKey} className="card p-4 text-center">
                <h5 className="text-sm font-semibold mb-1">{t(s.nameKey)}</h5>
                <p className="text-[10px] text-[var(--fg-dim)]">{t(s.descKey)}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Become a sponsor CTA */}
        <motion.div {...fade(0.2)} className="text-center mt-16">
          <div className="card p-8 max-w-2xl mx-auto">
            <h4 className="text-lg font-bold mb-2">{t("hero.sponsor.become_title")}</h4>
            <p className="text-sm text-[var(--fg-dim)] mb-4">
              {t("hero.sponsor.become_subtitle")}
            </p>
            <a
              href="mailto:kuangketongxue@gmail.com"
              className="text-[var(--accent)] hover:underline text-sm font-mono"
            >
              kuangketongxue@gmail.com
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
