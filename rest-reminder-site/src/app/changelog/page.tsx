"use client";

import { useEffect } from "react";
import { useI18n } from "@/lib/i18n";

const RELEASES = [
  {
    version: "v6.2.10",
    date: "2026-07-15",
    tagKey: "changelog.v6_2_10.tag",
    sections: [
      { titleKey: "changelog.v6_2_10.s1.title", itemKeys: ["changelog.v6_2_10.i1", "changelog.v6_2_10.i2", "changelog.v6_2_10.i3"] },
      { titleKey: "changelog.v6_2_10.s2.title", itemKeys: ["changelog.v6_2_10.i4", "changelog.v6_2_10.i5"] },
      { titleKey: "changelog.v6_2_10.s3.title", itemKeys: ["changelog.v6_2_10.i6"] },
    ],
  },
  {
    version: "v6.2.9",
    date: "2026-07-15",
    tagKey: "changelog.v6_2_9.tag",
    sections: [
      { titleKey: "changelog.v6_2_9.s1.title", itemKeys: ["changelog.v6_2_9.i1", "changelog.v6_2_9.i2", "changelog.v6_2_9.i3"] },
      { titleKey: "changelog.v6_2_9.s2.title", itemKeys: ["changelog.v6_2_9.i4", "changelog.v6_2_9.i5", "changelog.v6_2_9.i6"] },
    ],
  },
  {
    version: "v6.2.8",
    date: "2026-07-15",
    tagKey: "changelog.v6_2_8.tag",
    sections: [
      { titleKey: "changelog.v6_2_8.s1.title", itemKeys: ["changelog.v6_2_8.i1", "changelog.v6_2_8.i2"] },
      { titleKey: "changelog.v6_2_8.s2.title", itemKeys: ["changelog.v6_2_8.i3", "changelog.v6_2_8.i4"] },
    ],
  },
  {
    version: "v6.2.7",
    date: "2026-07-13",
    tagKey: "changelog.v6_2_7.tag",
    sections: [
      { titleKey: "changelog.v6_2_7.s1.title", itemKeys: ["changelog.v6_2_7.i1", "changelog.v6_2_7.i2", "changelog.v6_2_7.i3", "changelog.v6_2_7.i4", "changelog.v6_2_7.i5", "changelog.v6_2_7.i6"] },
    ],
  },
  {
    version: "v6.2.6",
    date: "2026-07-10",
    tagKey: "changelog.v6_2_6.tag",
    sections: [
      { titleKey: "changelog.v6_2_6.s1.title", itemKeys: ["changelog.v6_2_6.i1", "changelog.v6_2_6.i2", "changelog.v6_2_6.i3", "changelog.v6_2_6.i4", "changelog.v6_2_6.i5"] },
    ],
  },
];

export default function ChangelogPage() {
  const { t } = useI18n();

  useEffect(() => {
    document.title = t("changelog.title");
  }, [t]);

  return (
    <main className="flex-1">
      <div className="max-w-3xl mx-auto px-6 py-20 animate-[fadeInUp_0.5s_ease-out]">
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-2 font-display">
          {t("changelog.title")}
        </h1>
        <p className="text-[var(--fg-dim)] mb-12">{t("changelog.subtitle")}</p>

        <div className="space-y-12">
          {RELEASES.map((release) => (
            <article key={release.version} className="docs-card p-8">
              <div className="flex items-baseline gap-3 mb-4">
                <h2 className="text-2xl font-bold">{release.version}</h2>
                <span className="text-sm text-[var(--fg-dim)]">{release.date}</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-[var(--accent-soft)] text-[var(--accent)]">
                  {t(release.tagKey)}
                </span>
              </div>
              <div className="space-y-5">
                {release.sections.map((section) => (
                  <section key={section.titleKey}>
                    <h3 className="text-lg font-semibold mb-2">{t(section.titleKey)}</h3>
                    <ul className="space-y-1.5">
                      {section.itemKeys.map((itemKey) => (
                        <li key={itemKey} className="text-[var(--fg-dim)] text-sm flex gap-2">
                          <span className="text-[var(--accent)]">•</span>
                          <span>{t(itemKey)}</span>
                        </li>
                      ))}
                    </ul>
                  </section>
                ))}
              </div>
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}
