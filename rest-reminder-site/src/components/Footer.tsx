export default function Footer() {
  return (
    <footer className="bg-[var(--bg)] border-t border-[var(--border)]">
      {/* Hero CTA — WorkBuddy 风格 */}
      <div className="relative overflow-hidden">
        <div className="max-w-6xl mx-auto px-6 py-20 flex flex-col md:flex-row items-center gap-12">
          <div className="flex-1">
            <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-4 font-display text-[var(--fg)]">
              保护你的眼睛<br />
              <span className="text-[var(--accent)]">从每一次休息开始</span>
            </h2>
            <p className="text-base text-[var(--fg-dim)] leading-relaxed mb-8 max-w-lg">
              免费开始，零门槛。把休息提醒、护眼计时、学习追踪交给 Rest Reminder，专注力留给自己。
            </p>
            <a
              href="https://github.com/kuangketongxue/library-remind/releases/latest"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-[var(--accent)] text-white font-semibold px-8 py-3.5 rounded-lg text-sm hover:opacity-90 transition-opacity"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              立即下载
            </a>
          </div>
          <div className="flex-shrink-0 hidden md:block">
            <img src="/rest-reminder-logo.png" alt="Rest Reminder" className="w-40 h-40 rounded-2xl opacity-80" />
          </div>
        </div>
      </div>

      {/* 4-Column Footer — WorkBuddy 风格 */}
      <div className="border-t border-[var(--border)]">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-10">
            {/* 服务条款 */}
            <div>
              <h4 className="text-sm font-bold text-[var(--fg)] mb-4 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]"></span>
                服务条款
              </h4>
              <ul className="space-y-2.5">
                <li><a href="/terms" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">用户协议</a></li>
                <li><a href="/privacy" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">隐私政策</a></li>
                <li><a href="/rules" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">社区规则</a></li>
              </ul>
            </div>

            {/* 文档指引 */}
            <div>
              <h4 className="text-sm font-bold text-[var(--fg)] mb-4 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]"></span>
                文档指引
              </h4>
              <ul className="space-y-2.5">
                <li><a href="/docs" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">产品介绍</a></li>
                <li><a href="/docs#常见问题" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">常见问题</a></li>
                <li><a href="https://github.com/kuangketongxue/library-remind/blob/main/CHANGELOG.md" target="_blank" rel="noopener noreferrer" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">更新日志</a></li>
              </ul>
            </div>

            {/* 产品下载 */}
            <div>
              <h4 className="text-sm font-bold text-[var(--fg)] mb-4 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]"></span>
                产品下载
              </h4>
              <ul className="space-y-2.5">
                <li><a href="https://github.com/kuangketongxue/library-remind/releases/latest" target="_blank" rel="noopener noreferrer" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">Windows 下载</a></li>
                <li><a href="https://github.com/kuangketongxue/library-remind/releases" target="_blank" rel="noopener noreferrer" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">历史版本</a></li>
                <li><a href="/pricing" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">定价说明</a></li>
              </ul>
            </div>

            {/* 联系我们 */}
            <div>
              <h4 className="text-sm font-bold text-[var(--fg)] mb-4 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]"></span>
                联系我们
              </h4>
              <ul className="space-y-2.5">
                <li><a href="/contact" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">联系方式</a></li>
                <li><a href="https://github.com/kuangketongxue/library-remind/issues" target="_blank" rel="noopener noreferrer" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">问题反馈</a></li>
                <li><a href="https://github.com/kuangketongxue/library-remind" target="_blank" rel="noopener noreferrer" className="text-sm text-[var(--fg-dim)] hover:text-[var(--accent)] transition-colors">GitHub</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-[var(--border)]">
        <div className="max-w-6xl mx-auto px-6 py-5 flex flex-col md:flex-row justify-between items-center gap-3">
          <p className="text-xs text-[var(--fg-muted)]">
            © 2026 冬之街 · 基于 MIT 协议开源
          </p>
          <p className="text-xs text-[var(--fg-muted)]">
            Made with <span className="text-[var(--accent)]">♥</span> by 冬之街
          </p>
        </div>
      </div>
    </footer>
  );
}
