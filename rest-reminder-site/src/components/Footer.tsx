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
          <p className="text-xs font-semibold text-[var(--fg-dim)] uppercase tracking-wider mb-3">技术支持</p>
          <div className="flex items-center justify-center gap-6 flex-wrap">
            {[
              { name: "LongCat", url: "https://longcat.chat/platform/docs/zh/", desc: "图像生成" },
              { name: "StepFun", url: "https://platform.stepfun.com", desc: "大模型 / TTS" },
              { name: "SenseNova", url: "https://sensenova.cn", desc: "多模态大模型" },
              { name: "XiaomiMimo", url: "https://xiumimo.com", desc: "技术支持" },
              { name: "CC Switch", url: "https://ccswitch.io", desc: "AI 编程 CLI" },
            ].map((s) => (
              <a
                key={s.name}
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors"
                title={s.desc}
              >
                {s.name}
              </a>
            ))}
          </div>
          <p className="text-[10px] text-[var(--fg-muted)] mt-3">
            商务合作/赞助请联系{" "}
            <a href="mailto:kuangketongxue@gmail.com" className="text-[var(--accent)] hover:underline font-mono">
              kuangketongxue@gmail.com
            </a>
          </p>
        </div>
      </div>

      {/* Main footer */}
      <div className="border-t border-[var(--border)]">
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
