export default function Footer() {
  return (
    <footer className="bg-[var(--bg)] border-t border-[var(--border)]">
      {/* Main footer */}
      <div className="max-w-6xl mx-auto px-6 pt-12 pb-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-10">
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2.5 mb-4">
              <img src="/rest-reminder-logo.png" alt="Rest Reminder" className="w-8 h-8 rounded-md" />
              <span className="font-semibold text-base font-display">Rest Reminder</span>
            </div>
            <p className="text-sm text-[var(--fg-dim)] leading-relaxed mb-4">
              保护你的眼睛，从每一次休息开始。
            </p>
            <div className="flex items-center gap-3">
              <a
                href="https://github.com/kuangketongxue/library-remind"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors"
                aria-label="GitHub"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
              </a>
              <a
                href="mailto:kuangketongxue@gmail.com"
                className="text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors"
                aria-label="Email"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </a>
            </div>
          </div>
          <div className="footer-col">
            <h4>产品</h4>
            <a href="/docs">文档</a>
            <a href="#download">下载</a>
          </div>
          <div className="footer-col">
            <h4>资源</h4>
            <a href="https://github.com/kuangketongxue/library-remind/blob/main/CHANGELOG.md" target="_blank" rel="noopener noreferrer">更新日志</a>
            <a href="/docs#常见问题">常见问题</a>
            <a href="#sponsor">赞助商</a>
          </div>
          <div className="footer-col">
            <h4>社区</h4>
            <a href="https://github.com/kuangketongxue/library-remind" target="_blank" rel="noopener noreferrer">GitHub</a>
            <a href="mailto:kuangketongxue@gmail.com">商务合作</a>
            <a href="https://github.com/kuangketongxue/library-remind/issues" target="_blank" rel="noopener noreferrer">问题反馈</a>
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
            Made with <span className="text-[var(--accent)]">♥</span> by 冬之街
          </p>
        </div>
      </div>
    </footer>
  );
}
