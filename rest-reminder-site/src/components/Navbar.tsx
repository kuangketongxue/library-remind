import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[rgba(10,10,11,0.85)] backdrop-blur-xl border-b border-[var(--border)]">
      <div className="max-w-6xl mx-auto flex items-center justify-between h-16 px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <img src="/rest-reminder-logo.png" alt="Rest Reminder" className="w-8 h-8 rounded-md" />
          <span className="font-semibold text-[15px] font-display tracking-tight">Rest Reminder</span>
        </Link>

        <div className="flex items-center gap-6">
          <a href="/docs" className="text-[13px] text-[var(--fg-dim)] hover:text-[var(--fg)] transition-colors hidden md:block">
            文档
          </a>
          <a href="https://github.com/kuangketongxue/library-remind"
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
