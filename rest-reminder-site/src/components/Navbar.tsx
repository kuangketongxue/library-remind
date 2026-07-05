import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[rgba(10,10,11,0.85)] backdrop-blur-xl border-b border-[var(--border)]">
      <div className="max-w-6xl mx-auto flex items-center justify-between h-16 px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <img src="/rest-reminder-logo.png" alt="Rest Reminder" className="w-8 h-8 rounded-md" />
          <span className="font-semibold text-[15px] font-display tracking-tight text-white">Rest Reminder</span>
        </Link>

        <div className="flex items-center gap-5">
          <a href="/docs" className="text-[13px] text-white/70 hover:text-white transition-colors hidden md:block">
            文档
          </a>
          <a href="/pricing" className="text-[13px] text-white/70 hover:text-white transition-colors hidden md:block">
            定价
          </a>
          <a href="https://github.com/kuangketongxue/library-remind"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[13px] text-white/70 hover:text-white transition-colors hidden sm:block"
          >
            GitHub
          </a>
          <a
            href="/docs#搜索"
            className="hidden md:flex items-center gap-1.5 text-[12px] text-white/50 bg-white/8 border border-white/10 rounded-lg px-3 py-1.5 hover:bg-white/12 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8" /><path strokeLinecap="round" d="M21 21l-4.35-4.35" />
            </svg>
            搜索
            <kbd className="text-[10px] text-white/40 bg-white/6 rounded px-1 py-0.5 ml-1">Ctrl K</kbd>
          </a>
          <a href="#download" className="btn-primary px-4 py-1.5 text-[13px]">
            免费下载
          </a>
        </div>
      </div>
    </nav>
  );
}
