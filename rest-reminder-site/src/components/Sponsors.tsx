"use client";

const sponsors: { name: string; desc: string; url: string }[] = [];

export default function Sponsors() {
  return (
    <section className="py-20 px-6 border-t border-[var(--border)]" id="sponsors">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-center mb-3 font-display">感谢赞助商</h2>
        <p className="text-[var(--fg-dim)] text-center mb-10">感谢以下伙伴支持 Rest Reminder 的开发与运营。</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sponsors.map((s) => (
            <a key={s.name} href={s.url} target="_blank" rel="noopener noreferrer" className="border border-[var(--border)] rounded-xl p-6 block bg-[var(--surface)] hover:border-[var(--accent)] hover:bg-[var(--surface-hover)] transition-colors">
              <h3 className="text-[15px] font-semibold mb-1 tracking-tight">{s.name}</h3>
              <p className="text-[13px] text-[var(--fg-dim)] leading-relaxed">{s.desc}</p>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
