"use client";

const features = [
  {
    icon: "⏱️",
    title: "60 分钟专注循环",
    desc: "学习 60 分钟 → 5 分钟请辨倒计时（展示思辨金句） → 5 分钟休息 → 自动打开 B 站收藏夹视频。每 3 轮自动播放护眼视频，循环往复。"
  },
  {
    icon: "👁️",
    title: "20-20-20 护眼提醒",
    desc: "每 20 分钟弹出轻量浮窗，提醒看 6 米外 20 秒，15 秒自动消失。可拖动到任意位置，不打断学习流。"
  },
  {
    icon: "📊",
    title: "学习时长追踪与打卡",
    desc: "实时统计学习时长，连续打卡 + 里程碑金句（1-365 天）+ 每小时复盘评分。数据持久化到本地 JSON，趋势分析 5 标签页可视化。"
  },
  {
    icon: "📈",
    title: "趋势分析",
    desc: "5 标签页多维度图表：今日复盘时间线、周/月/季/年趋势柱状图、7×24 学习热力图。鼠标悬浮查看具体数值，帮你发现最佳学习时段。"
  },
  {
    icon: "🤖",
    title: "AI 学习分析",
    desc: "基于 SenseNova API 自动生成日报/周报/月报/季报/年报。每份报告 400+ 字，含概览/趋势/学科分布/改进建议/亮点总结五章。未配置 API 时降级为本地数据摘要。"
  },
  {
    icon: "🔒",
    title: "完全离线 · 隐私优先",
    desc: "核心功能无需联网，数据只存在本地 JSON 文件。MIT 开源协议，所有功能永久免费，无隐藏收费、无订阅、无数据上传。"
  },
];

const rows = [
  { feature: "休息提醒 + 护眼", rr: "✓", fq: "✗", xt: "✗" },
  { feature: "学习追踪 + 打卡", rr: "✓", fq: "✗", xt: "✗" },
  { feature: "趋势分析（5 标签页）", rr: "柱状图+热力图", fq: "✗", xt: "✗" },
  { feature: "AI 多维度报告", rr: "✓ (本地降级)", fq: "✗", xt: "✗" },
  { feature: "复盘评分（学科+标签）", rr: "✓", fq: "✗", xt: "✗" },
  { feature: "请辨金句 + 里程碑", rr: "✓", fq: "✗", xt: "✗" },
  { feature: "开机自启 + 静默启动", rr: "✓", fq: "✗", xt: "✓" },
  { feature: "电池充电监控", rr: "✓", fq: "✗", xt: "✗" },
  { feature: "数据本地存储", rr: "✓", fq: "部分", xt: "✗" },
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
        <div className="mt-20">
          <h3 className="text-xl font-bold mb-6 font-display">与其他方案对比</h3>
          <div className="border border-[var(--border)] overflow-hidden rounded-2xl">
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
      </div>
    </section>
  );
}
