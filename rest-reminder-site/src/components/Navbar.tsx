"use client";

import Link from "next/link";
import { useState } from "react";
import { useI18n } from "@/lib/i18n";
import { useTheme } from "@/lib/theme";

export default function Navbar() {
  const { locale, setLocale, t } = useI18n();
  const { theme, toggle } = useTheme();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[color-mix(in_srgb,var(--bg)_85%,transparent)] backdrop-blur-xl border-b border-[var(--border)]">
        <div className="max-w-6xl mx-auto flex items-center justify-between h-20 px-6">
          <Link href="/" className="flex items-center gap-3">
            <img src="/app-icon.png" alt="Rest Reminder" className="w-10 h-10 rounded-lg" />
            <span className="text-lg font-bold font-display text-[var(--fg)] hidden sm:block">Rest Reminder</span>
          </Link>

          {/* Desktop nav */}
          <div className="flex items-center gap-5">
            <a href="/docs" className="text-[13px] text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors hidden md:block">
              {t("nav.docs")}
            </a>
            <a href="/pricing" className="text-[13px] text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors hidden md:block">
              {t("nav.pricing")}
            </a>
            <a href="/contact" className="text-[13px] text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors hidden md:block">
              {t("nav.contact")}
            </a>

            {/* GitHub */}
            <a
              href="https://github.com/kuangketongxue/library-remind"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[13px] text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors hidden sm:flex items-center gap-1.5"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.385.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
              {t("nav.github")}
            </a>

            {/* Search */}
            <a
              href="/docs#搜索"
              className="hidden md:flex items-center gap-1.5 text-[12px] text-[var(--fg-dim)] bg-[var(--surface)] border border-[var(--border)] rounded-lg px-3 py-1.5 hover:bg-[var(--surface-hover)] transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8" /><path strokeLinecap="round" d="M21 21l-4.35-4.35" />
              </svg>
              {t("nav.search")}
              <kbd className="text-[10px] text-[var(--fg-muted)] bg-[var(--surface-hover)] rounded px-1 py-0.5 ml-1">{t("nav.search_shortcut")}</kbd>
            </a>

            {/* Language switcher */}
            <div className="hidden md:flex items-center border border-[var(--border)] rounded-lg overflow-hidden">
              {(["zh", "en", "ja"] as const).map((l) => (
                <button
                  key={l}
                  onClick={() => setLocale(l)}
                  aria-label={t("nav.language_switch")}
                  aria-pressed={locale === l}
                  className={`text-[12px] px-2 py-1 transition-colors ${locale === l ? "bg-[var(--accent-soft)] text-[var(--accent)]" : "text-[var(--fg-muted)] hover:text-[var(--fg)]"}`}
                >
                  {l.toUpperCase()}
                </button>
              ))}
            </div>

            {/* Theme switcher */}
            <button
              onClick={toggle}
              className="hidden md:flex items-center justify-center w-8 h-8 rounded-lg border border-[var(--border)] text-[var(--fg-dim)] hover:text-[var(--fg)] hover:bg-[var(--surface-hover)] transition-colors"
              aria-label="Toggle theme"
            >
              {theme === "light" ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25c0 5.385 4.365 9.75 9.75 9.75 2.138 0 4.118-.688 5.752-1.852z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
                </svg>
              )}
            </button>

            <a href="/#download" className="btn-primary px-4 py-1.5 text-[13px] hidden sm:block">
              {t("nav.download")}
            </a>

            {/* Hamburger — mobile only */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden flex items-center justify-center w-10 h-10 rounded-lg text-[var(--fg-dim)] hover:text-[var(--fg)] hover:bg-[var(--surface-hover)] transition-colors"
              aria-label="Toggle menu"
            >
              {mobileOpen ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile menu overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setMobileOpen(false)} />
          <div className="absolute top-20 left-0 right-0 bg-[var(--bg)] border-b border-[var(--border)] shadow-lg animate-[fadeInUp_0.2s_ease-out]">
            <div className="max-w-6xl mx-auto px-6 py-4 space-y-1">
              <a href="/docs" className="block py-2.5 text-sm text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors" onClick={() => setMobileOpen(false)}>
                {t("nav.docs")}
              </a>
              <a href="/pricing" className="block py-2.5 text-sm text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors" onClick={() => setMobileOpen(false)}>
                {t("nav.pricing")}
              </a>
              <a href="/contact" className="block py-2.5 text-sm text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors" onClick={() => setMobileOpen(false)}>
                {t("nav.contact")}
              </a>
              <a href="/changelog" className="block py-2.5 text-sm text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors" onClick={() => setMobileOpen(false)}>
                {t("footer.link_changelog")}
              </a>
              <div className="border-t border-[var(--border)] pt-3 mt-3 flex items-center gap-3">
                {/* Language */}
                <div className="flex items-center border border-[var(--border)] rounded-lg overflow-hidden">
                  {(["zh", "en", "ja"] as const).map((l) => (
                    <button
                      key={l}
                      onClick={() => { setLocale(l); }}
                      className={`text-[12px] px-2.5 py-1.5 transition-colors ${locale === l ? "bg-[var(--accent-soft)] text-[var(--accent)]" : "text-[var(--fg-muted)]"}`}
                    >
                      {l.toUpperCase()}
                    </button>
                  ))}
                </div>
                {/* Theme */}
                <button
                  onClick={toggle}
                  className="flex items-center justify-center w-8 h-8 rounded-lg border border-[var(--border)] text-[var(--fg-dim)]"
                  aria-label="Toggle theme"
                >
                  {theme === "light" ? "🌙" : "☀️"}
                </button>
                {/* GitHub */}
                <a
                  href="https://github.com/kuangketongxue/library-remind"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center w-8 h-8 rounded-lg border border-[var(--border)] text-[var(--fg-dim)]"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.385.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                  </svg>
                </a>
              </div>
              <a href="/#download" className="btn-primary block text-center py-2.5 text-sm mt-3" onClick={() => setMobileOpen(false)}>
                {t("nav.download")}
              </a>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
