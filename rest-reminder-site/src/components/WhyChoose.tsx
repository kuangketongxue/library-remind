"use client";

const reasons = [
  {
    icon: "⏱️",
    title: "60 分钟自动循环",
    desc: "专注 55 分钟 + 休息 5 分钟，到点自动弹出倒计时。不需要手动计时，也不需要记住该休息了。",
  },
  {
    icon: "👁️",
    title: "20-20-20 护眼",
    desc: "每 20 分钟提醒你看 20 英尺外 20 秒，眼科医生推荐的黄金法则，内嵌在计时周期里。",
  },
  {
    icon: "🎬",
    title: "B站护眼视频",
    desc: "休息时自动播放你收藏的 B站 放松视频，不用自己找内容，到点就能跟着做眼保健操。",
  },
  {
    icon: "📊",
    title: "学习数据追踪",
    desc: "自动记录每次学习时长、连续打卡天数、趋势变化。5 个标签页看懂你的学习模式。",
  },
  {
    icon: "🤖",
    title: "AI 学习分析",
    desc: "根据你的学习数据自动生成个性化报告和建议，不用自己总结，让数据替你复盘。",
  },
  {
    icon: "🪶",
    title: "48MB 不打扰",
    desc: "单文件安装，启动秒开，后台静默运行。不占内存，不弹广告，不打扰你正在做的事。",
  },
];

export default function WhyChoose() {
  return (
    <section className="py-20 px-6 section-glow">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl md:text-[2.5rem] font-extrabold tracking-tight mb-3 font-display">为什么选择 Rest Reminder</h2>
        <p className="text-[var(--fg-dim)] text-lg mb-10">不是又一个番茄钟，是为长时间学习/工作设计的护眼助手。</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reasons.map((r) => (
            <div key={r.title} className="border border-[var(--border)] rounded-xl p-6 bg-[var(--surface)] hover:border-[var(--accent)] hover:bg-[var(--surface-hover)] transition-colors">
              <div className="text-2xl mb-3">{r.icon}</div>
              <h3 className="text-[15px] font-semibold mb-1.5 tracking-tight">{r.title}</h3>
              <p className="text-[13px] text-[var(--fg-dim)] leading-relaxed">{r.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
