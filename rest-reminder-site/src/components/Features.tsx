"use client";

const features = [
  { icon: "", title: "20-20-20 护眼", desc: "每 20 分钟轻量浮窗提醒看远处，保护眼睛" },
  { icon: "", title: "智能循环计时", desc: "到时间自动提醒，休息完自动重启" },
  { icon: "", title: "活动密度感知", desc: "连续活跃缩至45min，空闲5min自动暂停" },
  { icon: "", title: "趋势分析", desc: "5标签页：今日/周/月/季年/时段趋势" },
  { icon: "", title: "请辨金句", desc: "15条思辨金句，每日不重复" },
  { icon: "", title: "AI 分析（Pro）", desc: "AI 深度分析学习数据，自动生成日报/周报/月报/季报/年报" },
];

const rows = [
  { feature: "休息提醒+护眼", rr: "✓", fq: "✗", xt: "✗" },
  { feature: "活动密度感知", rr: "✓", fq: "✗", xt: "✗" },
  { feature: "学习追踪+打卡", rr: "✓", fq: "仅今日", xt: "✗" },
  { feature: "趋势分析", rr: "5标签页", fq: "仅今日", xt: "✗" },
  { feature: "开机自启", rr: "✓", fq: "✗", xt: "✓" },
  { feature: "AI 分析+多维度报告", rr: "Pro", fq: "✗", xt: "✗" },
];

export default function Features() {
  return (
    <section className="py-20 px-6" id="features">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl md:text-[2.5rem] font-extrabold tracking-tight mb-3 font-display">核心功能</h2>
        <p className="text-[var(--fg-dim)] text-lg mb-12">免费版已满足日常需求，Pro 版提供更深度的 AI 分析。</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f) => (
            <div key={f.title} className="border border-[var(--border)] rounded-xl p-6 bg-[var(--surface)] hover:border-[var(--accent)] hover:bg-[var(--surface-hover)] transition-colors">
              <h3 className="text-[15px] font-semibold mb-1.5 tracking-tight">{f.title}</h3>
              <p className="text-[13px] text-[var(--fg-dim)] leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Comparison table */}
        <div className="mt-12 border border-[var(--border)] overflow-hidden">
          <div className="grid grid-cols-4 text-[11px] border-b border-[var(--border)]">
            <div className="p-3.5 text-[var(--fg-dim)] font-semibold tracking-wider uppercase">功能</div>
            <div className="p-3.5 text-center font-semibold text-[var(--accent)] bg-[var(--accent-soft)]">Rest Reminder</div>
            <div className="p-3.5 text-center text-[var(--fg-dim)]">其他番茄钟</div>
            <div className="p-3.5 text-center text-[var(--fg-dim)]">系统提醒</div>
          </div>
          {rows.map((r, i) => (
            <div key={i} className="grid grid-cols-4 text-[13px] border-b border-[var(--border)] last:border-b-0">
              <div className="p-3.5 text-[var(--fg-dim)]">{r.feature}</div>
              <div className="p-3.5 text-center text-[var(--accent)] font-medium bg-[var(--accent-soft)]">{r.rr}</div>
              <div className="p-3.5 text-center text-[var(--fg-dim)]">{r.fq}</div>
              <div className="p-3.5 text-center text-[var(--fg-dim)]">{r.xt}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
