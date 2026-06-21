"use client";

import { SectionHeader, FadeIn, ScaleIn } from "./Animations";

const plans = [
  {
    name: "免费版",
    price: "¥0",
    period: "永久免费",
    desc: "完整的休息提醒+学习追踪",
    features: [
      { text: "60分钟循环休息提醒", included: true },
      { text: "20-20-20 护眼提醒", included: true },
      { text: "活动密度感知+自动暂停", included: true },
      { text: "学习/电脑/休息时长追踪", included: true },
      { text: "连续打卡+里程碑金句", included: true },
      { text: "趋势分析（5标签页）", included: true },
      { text: "请辨金句+每小时复盘", included: true },
      { text: "开机自启+跨重启续接", included: true },
    ],
    cta: "免费下载",
    href: "#download",
    accent: false,
  },
  {
    name: "Pro",
    price: "¥19.9",
    period: "/月",
    desc: "AI 深度分析你的学习数据",
    badge: "🤖 AI 分析 + 多维度报告",
    features: [
      { text: "包含免费版全部功能", included: true },
      { text: "🤖 AI 学习数据分析", included: true, highlight: true },
      { text: "📅 日报/周报/月报自动生成", included: true, highlight: true },
      { text: "📈 季度/年度趋势报告", included: true, highlight: true },
      { text: "💡 个性化学习建议", included: true, highlight: true },
      { text: "📊 专注度评分统计", included: true, highlight: true },
    ],
    cta: "升级 Pro",
    href: "#",
    accent: true,
  },
];

export default function Pricing() {
  return (
    <section className="py-28 px-6 section-glow" id="pricing">
      <div className="max-w-6xl mx-auto">
        <SectionHeader label="定价" title="免费够用，Pro 更深入" subtitle="免费版已包含完整休息提醒功能。Pro 版新增 AI 分析 + 多维度报告，助你深度了解学习模式。" />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {plans.map((p, i) => (
            <ScaleIn key={p.name} delay={i * 0.15}>
              <div
                className={`card p-9 h-full ${
                  p.accent
                    ? 'bg-[var(--accent-soft)] animate-pulse-glow'
                    : ''
                }`}
              >
                {p.badge && (
                  <span className="tag mb-5 inline-block text-[11px]">{p.badge}</span>
                )}
                <h3 className="text-xl font-bold mb-1 font-display">{p.name}</h3>
                <p className="text-sm text-[var(--fg-dim)] mb-6">{p.desc}</p>

                <div className="flex items-baseline gap-1.5 mb-8">
                  <span className="text-4xl font-bold font-display">{p.price}</span>
                  <span className="text-sm text-[var(--fg-dim)]">{p.period}</span>
                </div>

                <ul className="space-y-3.5 mb-8">
                  {p.features.map((f: { text: string; included: boolean; highlight?: boolean }) => (
                    <li key={f.text} className={`flex items-start gap-3 text-sm ${f.included ? 'text-[var(--fg-dim)]' : 'text-[var(--fg-dim)] opacity-40'}`}>
                      <span className={`mt-0.5 ${(f as any).highlight ? 'text-[var(--accent)] font-bold' : 'text-[var(--accent)]'}`}>
                        {f.included ? '✓' : '✗'}
                      </span>
                      <span>{f.text}</span>
                    </li>
                  ))}
                </ul>

                <a
                  href={p.href}
                  className={`block text-center py-3.5 text-sm font-semibold ${
                    p.accent ? 'btn-primary btn-shine' : 'btn-ghost'
                  }`}
                >
                  {p.cta}
                </a>
              </div>
            </ScaleIn>
          ))}
        </div>

        <div className="text-center mt-8 text-sm text-[var(--fg-dim)]">
          免费版永久免费 · Pro 19.9元/月，随时取消
        </div>
      </div>
    </section>
  );
}
