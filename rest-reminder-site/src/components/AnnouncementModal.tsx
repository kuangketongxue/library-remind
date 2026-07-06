"use client";

import { useState, useEffect } from "react";

const ANNOUNCEMENT_KEY = "rest-reminder-announcement-v1";

export default function AnnouncementModal() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const seen = localStorage.getItem(ANNOUNCEMENT_KEY);
    if (!seen) {
      // 小延迟避免阻塞首屏渲染
      const t = setTimeout(() => setOpen(true), 800);
      return () => clearTimeout(t);
    }
  }, []);

  const dismiss = () => {
    setOpen(false);
    localStorage.setItem(ANNOUNCEMENT_KEY, "1");
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center">
      {/* 遮罩 */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={dismiss}
      />
      {/* 弹窗 */}
      <div className="relative bg-[var(--bg-card,#1a1a24)] border border-[var(--border,#2a2a35)] rounded-2xl shadow-2xl w-[90vw] max-w-[520px] p-8 animate-[fadeInUp_0.3s_ease-out]">
        {/* 关闭按钮 */}
        <button
          onClick={dismiss}
          className="absolute top-4 right-4 text-[var(--fg-dim,#666)] hover:text-[var(--fg,#e8e6e1)] transition-colors text-xl leading-none"
          aria-label="关闭"
        >
          ✕
        </button>

        {/* 标题 */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-xl">📢</span>
          <h2 className="text-lg font-bold">平台公告</h2>
        </div>

        {/* 内容 */}
        <div className="text-sm leading-relaxed space-y-4 mb-6">
          <p className="text-[var(--fg-dim,#999)]">
            感谢各位用户对 Rest Reminder 的支持！以下是近期重要更新：
          </p>

          <div>
            <p className="font-semibold mb-1">1. AI 学习报告修复</p>
            <ul className="list-disc list-inside text-[var(--fg-dim,#999)] space-y-0.5 ml-2">
              <li>修复 AI 服务不可用时报告只显示一条金句的问题</li>
              <li>现在会显示完整的学习数据摘要（时长、轮次、复盘记录）</li>
            </ul>
          </div>

          <div>
            <p className="font-semibold mb-1">2. 官网全面升级</p>
            <ul className="list-disc list-inside text-[var(--fg-dim,#999)] space-y-0.5 ml-2">
              <li>新增联系我们页面、定价页面、法律合规页面</li>
              <li>文档中心改版，新增搜索和快速导航</li>
            </ul>
          </div>

          <div>
            <p className="font-semibold mb-1">3. v6.2.5 发布</p>
            <ul className="list-disc list-inside text-[var(--fg-dim,#999)] space-y-0.5 ml-2">
              <li>关终端不再退出应用</li>
              <li>修复多个启动和部署相关问题</li>
            </ul>
          </div>
        </div>

        {/* 日期 + 按钮 */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-[var(--fg-muted,#555)]">2026年7月6日</span>
          <button
            onClick={dismiss}
            className="px-6 py-2 text-sm font-medium rounded-lg border border-[var(--accent,#d4af37)] text-[var(--accent,#d4af37)] hover:bg-[var(--accent-soft,rgba(212,175,55,0.1))] transition-colors"
          >
            我知道了
          </button>
        </div>
      </div>
    </div>
  );
}
