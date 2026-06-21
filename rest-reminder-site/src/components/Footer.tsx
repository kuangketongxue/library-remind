const sponsors = [
  { name: "Cloudflare", url: "https://cloudflare.com" },
  { name: "Supabase", url: "https://supabase.com" },
];

export default function Footer() {
  return (
    <footer className="bg-[var(--bg)]">
      {/* Sponsors bar */}
      <div className="border-t border-[var(--border)]">
        <div className="max-w-6xl mx-auto px-6 py-8 text-center">
          <p className="text-xs text-[var(--fg-dim)] mb-4">技术赞助</p>
          <div className="flex items-center justify-center gap-8">
            {sponsors.map((s) => (
              <a
                key={s.name}
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors font-medium"
              >
                {s.name}
              </a>
            ))}
          </div>
        </div>
      </div>

      {/* Main footer */}
      <div className="border-t border-[var(--border)]">
        <div className="max-w-6xl mx-auto px-6 pt-12 pb-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-10">
            <div className="col-span-2 md:col-span-1">
              <div className="flex items-center gap-2.5 mb-4">
                <div className="w-8 h-8 rounded-full bg-[var(--accent)] flex items-center justify-center text-[var(--bg)] text-sm font-bold font-display">R</div>
                <span className="font-semibold text-base font-display">Rest Reminder</span>
              </div>
              <p className="text-sm text-[var(--fg-dim)] leading-relaxed mb-4">
                保护你的眼睛，从每一次休息开始。
              </p>
            </div>
            <div className="footer-col">
              <h4>产品</h4>
              <a href="#features">功能</a>
              <a href="#pricing">定价</a>
              <a href="#download">下载</a>
            </div>
            <div className="footer-col">
              <h4>资源</h4>
              <a href="#changelog">更新日志</a>
              <a href="#faq">常见问题</a>
            </div>
            <div className="footer-col">
              <h4>社区</h4>
              <a href="https://github.com/kuangketongxue/library-remind" target="_blank" rel="noopener noreferrer">GitHub</a>
              <a href="https://afdian.com/a/kuangketongxue" target="_blank" rel="noopener noreferrer">赞助作者</a>
              <a href="https://github.com/kuangketongxue/library-remind/issues" target="_blank" rel="noopener noreferrer">问题反馈</a>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-[var(--border)]">
        <div className="max-w-6xl mx-auto px-6 py-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-xs text-[var(--fg-dim)]">
            © 2026 冬之街 · 基于 MIT 协议开源
          </p>
          <p className="text-xs text-[var(--fg-dim)]">
            Made with <span className="text-[var(--amber)]">♥</span> by 冬之街
          </p>
        </div>
      </div>
    </footer>
  );
}
