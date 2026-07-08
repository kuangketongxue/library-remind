"use client";

import { motion } from "framer-motion";
import { useI18n } from "@/lib/i18n";

const steps = [
  {
    num: "1",
    titleKey: "download.step1",
    descKey: "download.step1_desc",
    img: "/screenshot-download.png",
  },
  {
    num: "2",
    titleKey: "download.step2",
    descKey: "download.step2_desc",
    img: "/screenshot-main.png",
  },
  {
    num: "3",
    titleKey: "download.step3",
    descKey: "download.step3_desc",
    img: "/screenshot-stats.png",
  },
];

export default function Download() {
  const { t } = useI18n();
  return (
    <>
      {/* Installation steps */}
      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-14"
          >
            <p className="text-[var(--fg-dim)] text-lg">{t("download.subtitle")}</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((s, i) => (
              <motion.div
                key={s.num}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.15 }}
                className="text-center"
              >
                <div className="w-10 h-10 rounded-full bg-[var(--accent-soft)] text-[var(--accent)] text-sm font-bold flex items-center justify-center border border-[var(--border-accent)] mx-auto mb-4">
                  {s.num}
                </div>
                <h3 className="text-lg font-semibold mb-2">{t(s.titleKey)}</h3>
                <p className="text-sm text-[var(--fg-dim)] mb-5">{t(s.descKey)}</p>
                <img
                  src={s.img}
                  alt={t(s.titleKey)}
                  className="w-full max-w-[200px] mx-auto rounded-xl border border-[var(--border)] shadow-lg"
                  loading="lazy"
                />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA banner */}
      <section className="cta-banner py-24 px-6" id="download">
        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-6">
              <a
                href="https://github.com/kuangketongxue/library-remind/releases/latest"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-white text-[#b5651d] font-semibold px-8 py-3.5 rounded-full text-base hover:bg-[var(--fg)] hover:shadow-lg transition-all"
              >
                {t("download.cta_download")}
              </a>
              <a
                href="https://github.com/kuangketongxue/library-remind"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 border-2 border-white/40 text-white font-medium px-8 py-3.5 rounded-full text-base hover:border-white hover:bg-white/10 transition-all"
              >
                {t("download.cta_github")}
              </a>
            </div>
            <p className="text-white/70 text-sm">
              {t("download.note")}
            </p>
          </motion.div>
        </div>
      </section>
    </>
  );
}
