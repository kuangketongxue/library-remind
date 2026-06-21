"use client";

const testimonials = [
  {
    name: "等待你的评价",
    role: "下载使用后分享你的感受",
    text: "如果你正在使用 Rest Reminder，欢迎在 GitHub Issue 或官网留言分享你的使用体验，你的反馈会让这个工具变得更好。",
    stars: 5,
  },
  {
    name: "开源社区",
    role: "GitHub",
    text: "这是一个开源项目，欢迎提交 Issue 和 PR。你的贡献将帮助更多人保护眼睛。",
    stars: 5,
  },
  {
    name: "持续改进中",
    role: "每月更新",
    text: "如果你希望看到新功能（macOS 支持、更多主题、自定义提醒音等），请到 GitHub 提 Issue，我会认真考虑每一个建议。",
    stars: 5,
  },
];

export default function Testimonials() {
  return (
    <section className="py-20 px-6 section-glow">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-center mb-3 font-display">一起完善</h2>
        <p className="text-[var(--fg-dim)] text-center text-lg mb-10">这是一个社区驱动的开源项目，欢迎你的参与。</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {testimonials.map((t) => (
            <div key={t.name} className="border border-[var(--border)] rounded-xl p-6 bg-[var(--surface)] hover:border-[var(--accent)] hover:bg-[var(--surface-hover)] transition-colors">
              <div className="flex gap-0.5 mb-3">
                {Array.from({ length: t.stars }).map((_, i) => (
                  <span key={i} className="text-[var(--accent)] text-xs">&#9733;</span>
                ))}
              </div>
              <p className="text-[13px] text-[var(--fg-dim)] leading-relaxed mb-4">
                "{t.text}"
              </p>
              <div className="flex items-center gap-2.5 pt-3 border-t border-[var(--border)]">
                <div className="w-7 h-7 rounded-sm bg-[var(--surface-hover)] border border-[var(--border)] flex items-center justify-center text-[11px] text-[var(--fg-dim)] font-mono">
                  {t.name[0]}
                </div>
                <div>
                  <div className="font-medium text-[13px]">{t.name}</div>
                  <div className="text-[11px] text-[var(--fg-dim)]">{t.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
