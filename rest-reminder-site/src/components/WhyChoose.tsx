"use client";

const reasons = [
  { icon: "", title: "开源免费", desc: "MIT协议，核心功能永久免费。代码公开透明，社区驱动开发。" },
  { icon: "", title: "轻量极速", desc: "46MB单文件，启动秒开。不占内存，后台静默运行。" },
  { icon: "", title: "隐私优先", desc: "免费版完全离线，不联网不上传。你的数据只在你电脑上。" },
  { icon: "", title: "B站护眼", desc: "独家B站护眼视频联动，休息时自动播放你收藏的放松内容。" },
];

export default function WhyChoose() {
  return (
    <section className="py-20 px-6 section-glow">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl md:text-[2.5rem] font-extrabold tracking-tight mb-3 font-display">为什么选择 Rest Reminder</h2>
        <p className="text-[var(--fg-dim)] text-lg mb-10">不是又一个番茄钟，是为长时间学习/工作设计的护眼助手。</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {reasons.map((r) => (
            <div key={r.title} className="border border-[var(--border)] rounded-xl p-6 bg-[var(--surface)] hover:border-[var(--accent)] hover:bg-[var(--surface-hover)] transition-colors">
              <h3 className="text-[15px] font-semibold mb-1.5 tracking-tight">{r.title}</h3>
              <p className="text-[13px] text-[var(--fg-dim)] leading-relaxed">{r.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
