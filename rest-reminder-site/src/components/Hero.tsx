"use client";

import { motion } from "framer-motion";
import CountdownDemo from "./CountdownDemo";

const fade = (delay = 0) => ({
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] as const },
});

export default function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col justify-center px-6 pt-24 pb-16 overflow-hidden">
      {/* Subtle gradient background */}
      <div className="absolute top-[-20%] left-[-10%] w-[700px] h-[700px] rounded-full bg-[radial-gradient(circle,rgba(201,131,110,0.04)_0%,transparent_70%)] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-5%] w-[500px] h-[500px] rounded-full bg-[radial-gradient(circle,rgba(201,131,110,0.03)_0%,transparent_70%)] pointer-events-none" />

      <div className="relative z-10 max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* Left: Text */}
        <div>
          <motion.div {...fade(0)} className="inline-flex items-center gap-2 mb-8">
            <span className="tag">v4.0</span>
            <span className="text-sm text-[var(--fg-dim)]">开源免费 · MIT协议</span>
          </motion.div>

          <motion.h1
            {...fade(0.1)}
            className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-[-0.03em] leading-[1.05] mb-6 font-display"
          >
            久坐伤眼？
            <br />
            <span className="gradient-text">自动提醒你休息</span>
          </motion.h1>

          <motion.p
            {...fade(0.2)}
            className="text-lg text-[var(--fg-dim)] max-w-md leading-relaxed mb-10"
          >
            每小时自动提醒休息，追踪学习数据，AI 深度分析你的学习模式。
            <span className="block text-sm mt-3 text-[var(--accent)] font-medium">免费使用 · Pro 版仅 19.9元/月 解锁 AI 分析</span>
          </motion.p>

          <motion.div {...fade(0.3)} className="flex flex-col sm:flex-row gap-4">
            <a href="#download" className="btn-primary btn-shine px-8 py-3.5 text-base inline-flex items-center justify-center gap-2">
              ↓ 立即下载
            </a>
            <a href="#pricing" className="btn-ghost px-8 py-3.5 text-base inline-flex items-center justify-center">
              了解 Pro →
            </a>
          </motion.div>

          <motion.div {...fade(0.4)} className="flex gap-10 mt-12">
            <div>
              <div className="text-xl font-bold stat-number font-display">MIT</div>
              <div className="text-xs text-[var(--fg-dim)] mt-1">开源协议</div>
            </div>
            <div>
              <div className="text-xl font-bold stat-number font-display">0元</div>
              <div className="text-xs text-[var(--fg-dim)] mt-1">起步价</div>
            </div>
            <div>
              <div className="text-xl font-bold stat-number font-display">46MB</div>
              <div className="text-xs text-[var(--fg-dim)] mt-1">轻量安装</div>
            </div>
          </motion.div>
        </div>

        {/* Right: Interactive countdown demo */}
        <div className="flex justify-center lg:justify-end">
          <CountdownDemo />
        </div>
      </div>
    </section>
  );
}
