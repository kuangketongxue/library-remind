"use client";

import { motion } from "framer-motion";

const fade = (delay = 0) => ({
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] as const },
});

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center px-6 pt-20 pb-16 overflow-hidden">
      {/* Background video */}
      <video
        autoPlay
        muted
        loop
        playsInline
        className="absolute inset-0 w-full h-full object-cover opacity-30 pointer-events-none"
      >
        <source src="/promo_video.mp4" type="video/mp4" />
      </video>
      {/* Dark overlay for text readability */}
      <div className="absolute inset-0 bg-[var(--bg)]/60 pointer-events-none" />

      {/* Background glow */}
      <div className="absolute top-[10%] right-[5%] w-[500px] h-[500px] rounded-full bg-[radial-gradient(circle,rgba(245,158,11,0.06)_0%,transparent_70%)] pointer-events-none" />
      <div className="absolute bottom-[5%] left-[10%] w-[400px] h-[400px] rounded-full bg-[radial-gradient(circle,rgba(124,58,237,0.04)_0%,transparent_70%)] pointer-events-none" />

      <div className="relative z-10 max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        {/* Left: Text content */}
        <div>
          <motion.div {...fade(0)} className="inline-flex items-center gap-2 mb-6">
            <span className="text-[10px] font-semibold text-[var(--accent)] bg-[var(--accent-soft)] px-2.5 py-1 rounded-full border border-[var(--border-accent)]">
              开源免费 · MIT 协议
            </span>
            <span className="text-xs text-[var(--fg-dim)]">v5.9.0</span>
          </motion.div>

          <motion.h1
            {...fade(0.1)}
            className="text-4xl md:text-5xl lg:text-[3.5rem] font-extrabold tracking-[-0.03em] leading-[1.08] mb-5 font-display"
          >
            久坐伤眼？<br />
            <span className="text-[var(--accent)]">自动提醒你休息</span>
          </motion.h1>

          <motion.p
            {...fade(0.2)}
            className="text-base text-[var(--fg-dim)] max-w-md leading-relaxed mb-8"
          >
            46MB 轻量桌面挂件，60 分钟自动循环。右下角浮球实时显示倒计时，到点弹出护眼视频，AI 自动生成学习报告。
          </motion.p>

          <motion.div {...fade(0.3)} className="flex flex-col sm:flex-row gap-3 mb-10">
            <a href="#download" className="btn-primary px-7 py-3 text-sm inline-flex items-center justify-center gap-2">
              ↓ 免费下载
            </a>
            <a href="https://github.com/kuangketongxue/library-remind" target="_blank" rel="noopener noreferrer" className="btn-ghost px-7 py-3 text-sm inline-flex items-center justify-center gap-2">
              GitHub 开源 →
            </a>
          </motion.div>

          <motion.div {...fade(0.4)} className="flex gap-8">
            <div>
              <div className="text-lg font-bold font-display text-[var(--accent)]">0元</div>
              <div className="text-[11px] text-[var(--fg-dim)] mt-0.5">完全免费</div>
            </div>
            <div>
              <div className="text-lg font-bold font-display text-[var(--accent)]">46MB</div>
              <div className="text-[11px] text-[var(--fg-dim)] mt-0.5">轻量安装</div>
            </div>
            <div>
              <div className="text-lg font-bold font-display text-[var(--accent)]">MIT</div>
              <div className="text-[11px] text-[var(--fg-dim)] mt-0.5">开源协议</div>
            </div>
          </motion.div>
        </div>

        {/* Right: Hero banner image */}
        <motion.div {...fade(0.3)} className="flex justify-center lg:justify-end">
          <div className="relative w-full max-w-lg">
            <div className="relative rounded-2xl overflow-hidden border border-[var(--border)] shadow-2xl"
                 style={{ boxShadow: '0 0 80px rgba(245,158,11,0.06), 0 25px 50px rgba(0,0,0,0.4)' }}>
              <img src="/hero-banner.png" alt="Rest Reminder" className="w-full h-auto block" />
            </div>
            <div className="absolute -bottom-3 -right-3 bg-[var(--accent)] text-[var(--bg)] text-[10px] font-bold px-3 py-1.5 rounded-lg shadow-lg">
              开源免费 ✓
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
