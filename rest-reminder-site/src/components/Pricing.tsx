"use client";

import { SectionHeader, ScaleIn } from "./Animations";

const features = [
  { text: "60分钟循环休息提醒", included: true },
  { text: "20-20-20 护眼提醒", included: true },
  { text: "活动密度感知+自动暂停", included: true },
  { text: "学习/电脑/休息时长追踪", included: true },
  { text: "连续打卡+里程碑金句", included: true },
  { text: "趋势分析（5标签页）", included: true },
  { text: "AI 学习分析（日报/周报/月报/季报/年报）", included: true, highlight: true },
  { text: "开机自启+跨重启续接", included: true },
];

export default function Pricing() {
  return (
    <section className="py-28 px-6 section-glow" id="pricing">
      <div className="max-w-6xl mx-auto">
        <SectionHeader label="定价" title="完全免费，永久开源" subtitle="MIT 协议，所有功能直接可用，无隐藏收费、无订阅、无限制。" />

        <div className="max-w-2xl mx-auto">
          <ScaleIn>
            <div className="card p-9 text-center">
              <h3 className="text-3xl font-bold font-display mb-2">¥0</h3>
              <p className="text-sm text-[var(--fg-dim)] mb-8">永久免费 · MIT 开源</p>

              <ul className="space-y-3.5 mb-8 text-left max-w-sm mx-auto">
                {features.map((f) => (
                  <li key={f.text} className="flex items-start gap-3 text-sm text-[var(--fg-dim)]">
                    <span className={`mt-0.5 text-[var(--accent)] ${f.highlight ? 'font-bold' : ''}`}>
                      {f.included ? '✓' : '✗'}
                    </span>
                    <span className={f.highlight ? 'font-semibold text-[var(--fg)]' : ''}>{f.text}</span>
                  </li>
                ))}
              </ul>

              <a
                href="#download"
                className="inline-block py-3.5 px-8 text-sm font-semibold btn-primary btn-shine"
              >
                免费下载 ↓
              </a>
            </div>
          </ScaleIn>
        </div>
      </div>
    </section>
  );
}
