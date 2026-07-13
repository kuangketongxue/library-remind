"use client";

import { useEffect } from "react";
import { useI18n } from "@/lib/i18n";

export default function PrivacyChromePage() {
  const { t } = useI18n();

  useEffect(() => {
    document.title = t("privacy_chrome.h1");
  }, [t]);

  return (
    <main className="flex-1">
      <div className="max-w-3xl mx-auto px-6 py-20 animate-[fadeInUp_0.5s_ease-out]">
        <div className="docs-card p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-2 font-display">
            {t("privacy_chrome.h1")}
          </h1>
          <p className="text-sm text-[var(--fg-dim)] mb-8">
            {t("privacy_chrome.effective")}
          </p>

          <div className="space-y-8 text-[var(--fg)] leading-relaxed">
            <section>
              <h2 className="text-xl font-bold mb-3">{t("privacy_chrome.s1.title")}</h2>
              <p className="text-[var(--fg-dim)]">
                {t("privacy_chrome.s1.p1")}
                <strong>{t("privacy_chrome.s1.principle")}</strong>
                {t("privacy_chrome.s1.p2")}
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">{t("privacy_chrome.s2.title")}</h2>
              <p className="text-[var(--fg-dim)] mb-3">
                {t("privacy_chrome.s2.intro1")}
                <code className="bg-[var(--surface)] px-1.5 py-0.5 rounded text-xs font-mono text-[var(--accent)]">chrome.storage.local</code>
                {t("privacy_chrome.s2.intro2")}
              </p>
              <div className="space-y-2">
                {[
                  { name: "privacy_chrome.s2.r1Name", desc: "privacy_chrome.s2.r1Desc" },
                  { name: "privacy_chrome.s2.r2Name", desc: "privacy_chrome.s2.r2Desc" },
                  { name: "privacy_chrome.s2.r3Name", desc: "privacy_chrome.s2.r3Desc" },
                  { name: "privacy_chrome.s2.r4Name", desc: "privacy_chrome.s2.r4Desc" },
                  { name: "privacy_chrome.s2.r5Name", desc: "privacy_chrome.s2.r5Desc" },
                ].map(({ name, desc }) => (
                  <div key={name} className="flex gap-3 items-start">
                    <span className="text-[var(--accent)] mt-0.5">•</span>
                    <div>
                      <span className="font-medium text-sm">{t(name)}</span>
                      <span className="text-[var(--fg-dim)] text-sm"> — {t(desc)}</span>
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-[var(--fg-dim)] text-sm mt-3">
                <strong className="text-[var(--fg)]">{t("privacy_chrome.s2.note")}</strong>
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">{t("privacy_chrome.s3.title")}</h2>
              <p className="text-[var(--fg-dim)] mb-4">
                {t("privacy_chrome.s3.intro1")}
                <strong>{t("privacy_chrome.s3.introTrigger")}</strong>
                {t("privacy_chrome.s3.intro2")}
              </p>

              <div className="space-y-4">
                {[
                  {
                    title: "privacy_chrome.s3.1.title",
                    items: [
                      "privacy_chrome.s3.1.i1",
                      "privacy_chrome.s3.1.i2",
                      "privacy_chrome.s3.1.i3",
                      "privacy_chrome.s3.1.i4",
                    ],
                  },
                  {
                    title: "privacy_chrome.s3.2.title",
                    items: [
                      "privacy_chrome.s3.2.i1",
                      "privacy_chrome.s3.2.i2",
                      "privacy_chrome.s3.2.i3",
                    ],
                  },
                  {
                    title: "privacy_chrome.s3.3.title",
                    items: [
                      "privacy_chrome.s3.3.i1",
                      "privacy_chrome.s3.3.i2",
                      "privacy_chrome.s3.3.i3",
                      "privacy_chrome.s3.3.i4",
                    ],
                  },
                  {
                    title: "privacy_chrome.s3.4.title",
                    items: [
                      "privacy_chrome.s3.4.i1",
                      "privacy_chrome.s3.4.i2",
                      "privacy_chrome.s3.4.i3",
                    ],
                  },
                ].map(({ title, items }) => (
                  <div key={title} className="bg-[var(--surface)] rounded-lg p-5">
                    <h3 className="font-semibold mb-2">{t(title)}</h3>
                    <ul className="space-y-1">
                      {items.map((item) => (
                        <li key={item} className="text-sm text-[var(--fg-dim)] flex gap-2">
                          <span className="text-[var(--accent)]">•</span>
                          <span>{t(item)}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">{t("privacy_chrome.s4.title")}</h2>
              <div className="space-y-2 text-[var(--fg-dim)]">
                {[
                  "privacy_chrome.s4.i1",
                  "privacy_chrome.s4.i2",
                  "privacy_chrome.s4.i3",
                  "privacy_chrome.s4.i4",
                  "privacy_chrome.s4.i5",
                ].map((item) => (
                  <p key={item} className="flex gap-2 items-start">
                    <span className="text-[var(--accent)]">—</span>
                    <span>{t(item)}</span>
                  </p>
                ))}
              </div>
              <p className="mt-3 font-medium">
                {t("privacy_chrome.s4.close")}
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">{t("privacy_chrome.s5.title")}</h2>
              <p className="text-[var(--fg-dim)]">
                {t("privacy_chrome.s5.p1")}
                <a
                  href="https://github.com/kuangketongxue/library-remind"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[var(--accent)] hover:underline ml-1"
                >
                  {t("privacy_chrome.s5.url")}
                </a>
                {t("privacy_chrome.s5.p2")}
                <code className="bg-[var(--surface)] px-1.5 py-0.5 rounded text-xs font-mono text-[var(--accent)]">{t("privacy_chrome.s5.dir")}</code>
                {t("privacy_chrome.s5.p3")}
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">{t("privacy_chrome.s6.title")}</h2>
              <ul className="space-y-2 text-[var(--fg-dim)]">
                <li>• {t("privacy_chrome.s6.i1")}</li>
                <li>• {t("privacy_chrome.s6.i2")}</li>
                <li>• {t("privacy_chrome.s6.i3")}</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">{t("privacy_chrome.s7.title")}</h2>
              <ul className="space-y-2 text-[var(--fg-dim)]">
                <li>• <strong className="text-[var(--fg)]">{t("privacy_chrome.s7.1.label")}</strong>：{t("privacy_chrome.s7.1.text")}</li>
                <li>• <strong className="text-[var(--fg)]">{t("privacy_chrome.s7.2.label")}</strong>：{t("privacy_chrome.s7.2.text")}</li>
                <li>• <strong className="text-[var(--fg)]">{t("privacy_chrome.s7.3.label")}</strong>：{t("privacy_chrome.s7.3.text1")}<code className="bg-[var(--surface)] px-1 rounded text-xs font-mono">{t("privacy_chrome.s7.3.dir")}</code>{t("privacy_chrome.s7.3.text2")}</li>
                <li>• <strong className="text-[var(--fg)]">{t("privacy_chrome.s7.4.label")}</strong>：{t("privacy_chrome.s7.4.text")}</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">{t("privacy_chrome.s8.title")}</h2>
              <p className="text-[var(--fg-dim)]">
                {t("privacy_chrome.s8.body")}
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">{t("privacy_chrome.s9.title")}</h2>
              <p className="text-[var(--fg-dim)]">
                {t("privacy_chrome.s9.body")}
              </p>
            </section>

            <section className="border-t border-[var(--border)] pt-6">
              <h2 className="text-xl font-bold mb-3">{t("privacy_chrome.s10.title")}</h2>
              <div className="space-y-2 text-[var(--fg-dim)]">
                <p>
                  • <strong className="text-[var(--fg)]">{t("privacy_chrome.s10.emailLabel")}</strong>：
                  <a href="mailto:kuangketongxue@gmail.com" className="text-[var(--accent)] hover:underline">
                    kuangketongxue@gmail.com
                  </a>
                </p>
                <p>
                  • <strong className="text-[var(--fg)]">{t("privacy_chrome.s10.ghLabel")}</strong>：
                  <a
                    href="https://github.com/kuangketongxue/library-remind/issues"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[var(--accent)] hover:underline"
                  >
                    {t("privacy_chrome.s10.ghUrl")}
                  </a>
                </p>
              </div>
            </section>

            <p className="text-xs text-[var(--fg-muted)] pt-4">
              {t("privacy_chrome.footer.p1")}{" "}
              <a href="https://crazy-rest-reminder.pages.dev" target="_blank" rel="noopener noreferrer" className="text-[var(--accent)] hover:underline">
                {t("privacy_chrome.footer.url")}
              </a>
              {t("privacy_chrome.footer.p2")}{" "}
              <code className="bg-[var(--surface)] px-1 rounded text-xs font-mono">{t("privacy_chrome.footer.privacyUrl")}</code>
              {t("privacy_chrome.footer.p3")}
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
