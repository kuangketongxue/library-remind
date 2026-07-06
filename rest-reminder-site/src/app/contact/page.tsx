"use client";

export default function ContactPage() {
  return (
    <main className="flex-1">
      <div className="max-w-3xl mx-auto px-6 py-20 animate-[fadeInUp_0.5s_ease-out]">
        <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">联系我们</h1>
        <p className="text-[var(--fg-dim)] mb-12">无论你是用户、开发者还是合作伙伴，我们都欢迎你的来信。</p>

        {/* 邮箱 */}
        <div className="docs-card p-8 mb-8 animate-[fadeInUp_0.5s_ease-out_0.1s_both]">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-[var(--accent-soft)] flex items-center justify-center">
              <svg className="w-6 h-6 text-[var(--accent)]" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-bold">邮箱</h3>
              <p className="text-sm text-[var(--fg-dim)]">商务合作、问题反馈、建议都可以发邮件</p>
            </div>
          </div>
          <a
            href="mailto:kuangketongxue@gmail.com?subject=Rest%20Reminder%20-%20商务合作"
            className="inline-flex items-center gap-2 text-[var(--accent)] font-semibold text-lg hover:underline"
          >
            kuangketongxue@gmail.com
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
            </svg>
          </a>
        </div>

        {/* 微信 */}
        <div className="docs-card p-8 mb-8 animate-[fadeInUp_0.5s_ease-out_0.2s_both]">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-[var(--accent-soft)] flex items-center justify-center">
              <span className="text-xl">💬</span>
            </div>
            <div>
              <h3 className="text-lg font-bold">微信</h3>
              <p className="text-sm text-[var(--fg-dim)]">扫码添加微信，注明「Rest Reminder」</p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <img src="/wechat-pay.jpg" alt="微信二维码" className="w-32 h-32 rounded-lg border border-[var(--border)]" />
            <p className="text-sm text-[var(--fg-dim)]">添加后可以直接发消息咨询，回复更快</p>
          </div>
        </div>

        {/* GitHub */}
        <div className="docs-card p-8 mb-8 animate-[fadeInUp_0.5s_ease-out_0.3s_both]">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-[var(--accent-soft)] flex items-center justify-center">
              <svg className="w-6 h-6 text-[var(--accent)]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-bold">GitHub</h3>
              <p className="text-sm text-[var(--fg-dim)]">提交 Issue、提 PR、参与讨论</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-3">
            <a
              href="https://github.com/kuangketongxue/library-remind/issues/new?template=bug_report.md"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm font-medium text-[var(--accent)] border border-[var(--accent)] rounded-lg px-4 py-2 hover:bg-[var(--accent-soft)] transition-colors"
            >
              🐛 报告 Bug
            </a>
            <a
              href="https://github.com/kuangketongxue/library-remind/issues/new?template=feature_request.md"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm font-medium text-[var(--accent)] border border-[var(--accent)] rounded-lg px-4 py-2 hover:bg-[var(--accent-soft)] transition-colors"
            >
              ✨ 功能建议
            </a>
            <a
              href="https://github.com/kuangketongxue/library-remind/issues/new?template=partnership.md"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm font-medium text-[var(--accent)] border border-[var(--accent)] rounded-lg px-4 py-2 hover:bg-[var(--accent-soft)] transition-colors"
            >
              🤝 商务合作
            </a>
          </div>
        </div>

        {/* 回复时间 */}
        <div className="text-center text-sm text-[var(--fg-muted)] mt-12 animate-[fadeInUp_0.5s_ease-out_0.4s_both]">
          <p>通常 24 小时内回复 · 紧急问题请走 GitHub Issues</p>
        </div>
      </div>
    </main>
  );
}
