import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[rgba(10,10,11,0.85)] backdrop-blur-xl border-b border-[var(--border)]">
      <div className="max-w-6xl mx-auto flex items-center justify-between h-16 px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-md bg-[var(--accent)] flex items-center justify-center text-[var(--bg)] text-sm font-bold font-display">R</div>
          <span className="font-semibold text-[15px] font-display tracking-tight">Rest Reminder</span>
        </Link>

        <div className="flex items-center gap-6">
          <a href="#features" className="text-[13px] text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors hidden sm:block">
            功能
          </a>
          <a href="#changelog" className="text-[13px] text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors hidden md:block">
            更新日志
          </a>
          <a href="#faq" className="text-[13px] text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors hidden md:block">
            FAQ
          </a>
          <a
            href="https://github.com/kuangketongxue/library-remind"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[13px] text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors hidden sm:block"
          >
            GitHub
          </a>
          <a href="#download" className="btn-primary px-4 py-1.5 text-[13px]">
            免费下载
          </a>
        </div>
      </div>
    </nav>
  );
}
