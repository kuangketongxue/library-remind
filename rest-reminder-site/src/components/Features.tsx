"use client";

const features = [
  { icon: "⏱️", title: "智能循环计时", desc: "60分钟学习 → 5分钟倒计时 → 5分钟休息，自动循环不打断" },
  { icon: "👁️", title: "20-20-20 护眼提醒", desc: "每20分钟轻量浮窗提醒看远处，保护眼睛不累" },
  { icon: "📊", title: "学习时长追踪", desc: "学习/电脑/休息时长实时统计，连续打卡+里程碑金句" },
  { icon: "📈", title: "趋势分析", desc: "5标签页：今日/周/月/季年/时段趋势，数据可视化一目了然" },
  { icon: "💡", title: "请辨金句", desc: "休息时展示思辨金句，每日不重复，边休息边思考" },
  { icon: "🤖", title: "AI 学习分析", desc: "AI自动生成日报/周报/月报/季报/年报，分析你的学习模式" },
];

const rows = [
  { feature: "休息提醒+护眼", rr: "✓", fq: "✗", xt: "✗" },
  { feature: "学习追踪+打卡", rr: "✓", fq: "✗", xt: "✗" },
  { feature: "趋势分析", rr: "5标签页", fq: "✗", xt: "✗" },
  { feature: "AI 分析+多维度报告", rr: "✓", fq: "✗", xt: "✗" },
  { feature: "开机自启", rr: "✓", fq: "✗", xt: "✓" },
];

export default function Features() {
  return (
    <section className="py-24 px-6" id="features">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl md:text-[2.5rem] font-extrabold tracking-tight mb-3 font-display">核心功能</h2>
        <p className="text-[var(--fg-dim)] text-lg mb-14">所有功能完全免费，无隐藏收费。</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((f, i) => (
            <div key={f.title} className="card p-7 group">
              <div className="text-3xl mb-4 group-hover:scale-110 transition-transform duration-300">{f.icon}</div>
              <h3 className="text-[15px] font-semibold mb-2 tracking-tight">{f.title}</h3>
              <p className="text-[13px] text-[var(--fg-dim)] leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Comparison table */}
        <div className="mt-16 border border-[var(--border)] overflow-hidden rounded-2xl">
          <div className="grid grid-cols-4 text-[11px] border-b border-[var(--border)]">
            <div className="p-4 text-[var(--fg-dim)] font-semibold tracking-wider uppercase">功能</div>
            <div className="p-4 text-center font-semibold text-[var(--accent)] bg-[var(--accent-soft)]">Rest Reminder</div>
            <div className="p-4 text-center text-[var(--fg-dim)]">其他番茄钟</div>
            <div className="p-4 text-center text-[var(--fg-dim)]">系统提醒</div>
          </div>
          {rows.map((r, i) => (
            <div key={i} className="grid grid-cols-4 text-[13px] border-b border-[var(--border)] last:border-b-0 hover:bg-[var(--surface-hover)] transition-colors">
              <div className="p-4 text-[var(--fg-dim)]">{r.feature}</div>
              <div className="p-4 text-center text-[var(--accent)] font-medium bg-[var(--accent-soft)]">{r.rr}</div>
              <div className="p-4 text-center text-[var(--fg-dim)]">{r.fq}</div>
              <div className="p-4 text-center text-[var(--fg-dim)]">{r.xt}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
