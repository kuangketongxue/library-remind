"use client";

import { useRef, useEffect } from "react";
import { useI18n } from "@/lib/i18n";

export default function Hero() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const playingRef = useRef(false);
  const { t } = useI18n();

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;

    const tryPlay = async () => {
      if (playingRef.current) return;
      try {
        await v.play();
        playingRef.current = true;
      } catch {
        playingRef.current = false;
      }
    };

    if (v.readyState >= 2) {
      tryPlay();
    } else {
      v.addEventListener("canplay", tryPlay, { once: true });
    }

    const unlock = () => {
      if (!playingRef.current) tryPlay();
    };
    document.addEventListener("click", unlock, { once: true });

    return () => {
      v.removeEventListener("canplay", tryPlay);
      document.removeEventListener("click", unlock);
    };
  }, []);

  return (
    <section className="relative min-h-[92vh] flex flex-col items-center justify-center px-6 pt-24 pb-16 text-center overflow-hidden">
      {/* Video — poster shows until video loads, then video covers it */}
      <video
        ref={videoRef}
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
        poster="/hero-banner.webp"
        aria-label={t("hero.video.alt")}
        className="absolute inset-0 w-full h-full object-cover -z-10"
      >
        <source src="/promo_video.mp4" type="video/mp4" />
      </video>

      {/* Dark overlay — ensures text readability */}
      <div className="absolute inset-0 bg-black/50 -z-[5]" />

      {/* Subtle top glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] rounded-full bg-[radial-gradient(circle,rgba(245,158,11,0.05)_0%,transparent_60%)] pointer-events-none" />

      <div className="relative z-10 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 mb-5">
          <span className="text-[11px] font-semibold text-[var(--accent)] bg-[var(--accent-soft)] px-3 py-1 rounded-full border border-[var(--border)]">
            {t("hero.badge")}
          </span>
          <span className="text-xs text-white/70">v6.2.10</span>
        </div>

        <h1
          className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-[-0.03em] leading-[1.08] mb-5 font-display animate-[fadeInUp_0.6s_ease-out]"
          style={{ color: "#fff", textShadow: "0 2px 12px rgba(0,0,0,0.5)" }}
        >
          {t("hero.title_1")}
          <br />
          <span style={{ color: "var(--accent)", textShadow: "0 2px 8px rgba(0,0,0,0.4)" }}>
            {t("hero.title_2")}
          </span>
        </h1>

        <p
          className="text-base md:text-lg max-w-xl mx-auto leading-relaxed mb-8 animate-[fadeInUp_0.6s_ease-out_0.1s_both]"
          style={{ color: "rgba(255,255,255,0.85)", textShadow: "0 1px 6px rgba(0,0,0,0.4)" }}
        >
          {t("hero.desc")}
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-12 animate-[fadeInUp_0.6s_ease-out_0.2s_both]">
          <a href="#download" className="btn-primary px-8 py-3.5 text-sm inline-flex items-center justify-center gap-2">
            {t("hero.cta_download")}
          </a>
          <a
            href="https://github.com/kuangketongxue/library-remind"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost px-8 py-3.5 text-sm inline-flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.385.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            {t("hero.cta_github")}
          </a>
        </div>

        <div className="flex items-center justify-center gap-8 text-left animate-[fadeInUp_0.6s_ease-out_0.3s_both]">
          <div>
            <div className="text-xl font-bold font-display text-[var(--accent)]">48MB</div>
            <div className="text-xs text-white/60 mt-0.5">{t("hero.stat_48mb")}</div>
          </div>
          <div className="w-px h-8 bg-white/20" />
          <div>
            <div className="text-xl font-bold font-display text-[var(--accent)]">60min</div>
            <div className="text-xs text-white/60 mt-0.5">{t("hero.stat_60min")}</div>
          </div>
          <div className="w-px h-8 bg-white/20" />
          <div>
            <div className="text-xl font-bold font-display text-[var(--accent)]">MIT</div>
            <div className="text-xs text-white/60 mt-0.5">{t("hero.stat_mit")}</div>
          </div>
        </div>

        {/* 认证徽章 */}
        <div className="flex flex-col items-center gap-3 mt-8 animate-[fadeInUp_0.6s_ease-out_0.4s_both]">
          <img src="/fable5-verified.png" alt="Fable 5 Verified" className="w-full max-w-sm rounded-xl border border-white/10" />
          <img src="/gptsol-verified.jpg" alt="GPT Sol Verified" className="w-full max-w-xs rounded-xl border border-white/10" />
        </div>
      </div>
    </section>
  );
}
