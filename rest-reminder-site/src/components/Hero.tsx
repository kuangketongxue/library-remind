"use client";

import { useRef, useState, useEffect } from "react";

export default function Hero() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;

    // 强制尝试播放（绕过浏览器 autoplay 限制）
    const tryPlay = async () => {
      try {
        await v.play();
        setPlaying(true);
      } catch {
        // autoplay 被阻止 → 保持 poster 可见，等用户交互后再播
        setPlaying(false);
      }
    };

    // 视频已缓存就直接播
    if (v.readyState >= 2) {
      tryPlay();
    } else {
      v.addEventListener("canplay", tryPlay, { once: true });
    }

    // 用户点击页面任意位置触发播放（解锁 autoplay 限制）
    const unlock = () => {
      if (!playing) tryPlay();
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
        poster="/hero-banner.png"
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
          <span className="text-[11px] font-semibold text-[var(--accent)] bg-[var(--accent-soft)] px-3 py-1 rounded-full border border-[var(--border-accent)]">
            开源免费 · MIT 协议
          </span>
          <span className="text-xs text-white/70">v6.2.6</span>
        </div>

        <h1
          className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-[-0.03em] leading-[1.08] mb-5 font-display animate-[fadeInUp_0.6s_ease-out]"
          style={{ color: "#fff", textShadow: "0 2px 12px rgba(0,0,0,0.5)" }}
        >
          久坐伤眼？
          <br />
          <span style={{ color: "#d4a853", textShadow: "0 2px 8px rgba(0,0,0,0.4)" }}>
            自动提醒你休息
          </span>
        </h1>

        <p
          className="text-base md:text-lg max-w-xl mx-auto leading-relaxed mb-8 animate-[fadeInUp_0.6s_ease-out_0.1s_both]"
          style={{ color: "rgba(255,255,255,0.85)", textShadow: "0 1px 6px rgba(0,0,0,0.4)" }}
        >
          48MB 轻量桌面挂件，60 分钟专注循环。右下角浮球实时倒计时，到点弹出护眼视频，AI 自动生成学习报告。
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-12 animate-[fadeInUp_0.6s_ease-out_0.2s_both]">
          <a href="#download" className="btn-primary px-8 py-3.5 text-sm inline-flex items-center justify-center gap-2">
            ↓ 免费下载
          </a>
          <a
            href="https://github.com/kuangketongxue/library-remind"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost px-8 py-3.5 text-sm inline-flex items-center justify-center gap-2"
          >
            GitHub 开源 →
          </a>
        </div>

        <div className="flex items-center justify-center gap-8 text-left animate-[fadeInUp_0.6s_ease-out_0.3s_both]">
          <div>
            <div className="text-xl font-bold font-display text-[var(--accent)]">48MB</div>
            <div className="text-xs text-white/60 mt-0.5">轻量安装</div>
          </div>
          <div className="w-px h-8 bg-white/20" />
          <div>
            <div className="text-xl font-bold font-display text-[var(--accent)]">60min</div>
            <div className="text-xs text-white/60 mt-0.5">自动循环</div>
          </div>
          <div className="w-px h-8 bg-white/20" />
          <div>
            <div className="text-xl font-bold font-display text-[var(--accent)]">MIT</div>
            <div className="text-xs text-white/60 mt-0.5">开源协议</div>
          </div>
        </div>
      </div>
    </section>
  );
}
