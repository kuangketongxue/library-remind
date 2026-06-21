"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";

export default function CountdownDemo() {
  const [seconds, setSeconds] = useState(58 * 60 + 47); // start at 58:47
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    if (isPaused || seconds <= 0) return;
    const timer = setInterval(() => setSeconds((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(timer);
  }, [isPaused, seconds]);

  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  const progress = ((60 * 60 - seconds) / (60 * 60)) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8, delay: 0.6 }}
      className="relative inline-flex flex-col items-center"
    >
      {/* Ring */}
      <div className="relative w-40 h-40">
        <svg className="w-full h-full" viewBox="0 0 100 100">
          {/* Background ring */}
          <circle cx="50" cy="50" r="45" fill="none" stroke="var(--border)" strokeWidth="4" />
          {/* Progress ring */}
          <circle
            cx="50" cy="50" r="45"
            fill="none"
            stroke="var(--accent)"
            strokeWidth="4"
            strokeLinecap="round"
            className="countdown-ring"
            style={{ strokeDashoffset: 283 - (283 * progress) / 100 }}
          />
        </svg>
        {/* Time display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold font-display text-[var(--fg)]">
            {String(mins).padStart(2, "0")}:{String(secs).padStart(2, "0")}
          </span>
          <span className="text-xs text-[var(--fg-dim)] mt-1">距离下次休息</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex gap-3 mt-4">
        <button
          onClick={() => setIsPaused(!isPaused)}
          className="px-4 py-1.5 text-xs rounded-full border border-[var(--border)] text-[var(--fg-dim)] hover:border-[var(--accent)] hover:text-[var(--accent)] transition-colors"
        >
          {isPaused ? "▶ 继续" : "⏸ 暂停"}
        </button>
        <button
          onClick={() => { setSeconds(60 * 60); setIsPaused(false); }}
          className="px-4 py-1.5 text-xs rounded-full border border-[var(--border)] text-[var(--fg-dim)] hover:border-[var(--accent)] hover:text-[var(--accent)] transition-colors"
        >
          ↻ 重置
        </button>
      </div>

      {/* Status */}
      <div className="mt-3 text-xs text-[var(--fg-dim)] flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-[var(--accent)] animate-pulse" />
        {isPaused ? "已暂停" : "正在计时..."}
      </div>
    </motion.div>
  );
}
