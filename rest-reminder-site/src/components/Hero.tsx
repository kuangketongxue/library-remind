"use client";

import { motion } from "framer-motion";

const fade = (delay = 0) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] as const },
});

export default function Hero() {
  return (
    <section className="relative min-h-[92vh] flex flex-col items-center justify-center px-6 pt-24 pb-16 text-center">
      {/* Subtle top glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] rounded-full bg-[radial-gradient(circle,rgba(245,158,11,0.05)_0%,transparent_60%)] pointer-events-none" />

      <div className="relative z-10 max-w-3xl mx-auto">
        <motion.div {...fade(0)} className="inline-flex items-center gap-2 mb-5">
          <span className="text-[11px] font-semibold text-[var(--accent)] bg-[var(--accent-soft)] px-3 py-1 rounded-full border border-[var(--border-accent)]">
            开源免费 · MIT 协议
          </span>
          <span className="text-xs text-[var(--fg-dim)]">v6.1.6</span>
        </motion.div>

        <motion.h1
          {...fade(0.1)}
          className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-[-0.03em] leading-[1.08] mb-5 font-display"
        >
          久坐伤眼？<br />
          <span className="text-[var(--accent)]">自动提醒你休息</span>
        </motion.h1>

        <motion.p
          {...fade(0.2)}
          className="text-base md:text-lg text-[var(--fg-dim)] max-w-xl mx-auto leading-relaxed mb-8"
        >
          48MB 轻量桌面挂件，60 分钟专注循环。右下角浮球实时倒计时，到点弹出护眼视频，AI 自动生成学习报告。
        </motion.p>

        <motion.div {...fade(0.3)} className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-12">
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
        </motion.div>

        <motion.div {...fade(0.4)} className="flex items-center justify-center gap-8 text-left">
          <div>
            <div className="text-xl font-bold font-display text-[var(--accent)]">48MB</div>
            <div className="text-xs text-[var(--fg-dim)] mt-0.5">轻量安装</div>
          </div>
          <div className="w-px h-8 bg-[var(--border)]" />
          <div>
            <div className="text-xl font-bold font-display text-[var(--accent)]">60min</div>
            <div className="text-xs text-[var(--fg-dim)] mt-0.5">自动循环</div>
          </div>
          <div className="w-px h-8 bg-[var(--border)]" />
          <div>
            <div className="text-xl font-bold font-display text-[var(--accent)]">MIT</div>
            <div className="text-xs text-[var(--fg-dim)] mt-0.5">开源协议</div>
          </div>
        </motion.div>
      </div>

      {/* Hero screenshot */}
      <motion.div {...fade(0.35)} className="relative z-10 mt-16 w-full max-w-4xl mx-auto">
        <div className="relative rounded-xl overflow-hidden border border-[var(--border)] bg-[var(--surface)] shadow-2xl"
             style={{ boxShadow: '0 25px 60px rgba(0,0,0,0.35)' }}>
          <img src="/hero-banner.png" alt="Rest Reminder" className="w-full h-auto block" />
        </div>
      </motion.div>
    </section>
  );
}
