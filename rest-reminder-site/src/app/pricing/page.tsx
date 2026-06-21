import Link from "next/link";

const whyUpgrade = [
  {
    title: "看清你的学习轨迹",
    free: "只看今日数据，关了就没了",
    pro: "历史数据永久保存，周报月报一目了然",
  },
  {
    title: "节奏你说了算",
    free: "固定60分钟，不管你在做什么",
    pro: "15分钟冲刺/2小时深度工作，随时切换",
  },
  {
    title: "数据永不丢失",
    free: "数据存在本地，换电脑就没了",
    pro: "云端同步，换设备也能继续追踪",
  },
];

const faqs = [
  { q: "可以先免费试用Pro吗？", a: "可以。新用户注册后自动获得7天免费Pro试用，到期后自动降级为免费版，数据保留。" },
  { q: "免费版有什么限制？", a: "免费版固定60分钟提醒间隔，只显示今日学习数据。Pro版支持自定义间隔、历史数据保存、周报月报。" },
  { q: "订阅后可以退款吗？", a: "订阅后7天内可申请全额退款，无条件。7天后按剩余天数比例退款。" },
  { q: "数据安全吗？", a: "免费版数据100%本地存储。Pro版云同步数据加密存储于Supabase，只有你本人可访问。" },
  { q: "怎么取消订阅？", a: "在App设置中一键取消。取消后当前订阅期仍有效，到期后自动停止扣费。" },
  { q: "推荐返利怎么用？", a: "在设置中生成你的专属推荐码，分享给朋友。朋友订阅Pro后，你们双方各获得7天免费Pro。" },
];

const plans = [
  {
    name: "免费版",
    price: "¥0",
    period: "永久免费",
    desc: "完整的休息提醒+学习追踪",
    features: [
      "60分钟循环休息提醒",
      "20-20-20 护眼提醒",
      "活动密度感知+自动暂停",
      "学习/电脑/休息时长追踪",
      "连续打卡+里程碑金句",
      "趋势分析（5标签页）",
      "请辨金句+每小时复盘",
      "开机自启+跨重启续接",
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
    badge: "AI 分析 + 多维度报告",
    features: [
      { text: "包含免费版全部功能", highlight: true },
      { text: "AI 学习数据分析", highlight: true },
      { text: "日报/周报/月报自动生成", highlight: true },
      { text: "季度/年度趋势报告", highlight: true },
      { text: "个性化学习建议", highlight: true },
      { text: "专注度评分统计", highlight: true },
    ],
    cta: "升级 Pro",
    href: "#",
    accent: true,
  },
];

export { whyUpgrade, faqs, plans };

export default function PricingPage() {
  return (
    <main className="flex-1">
      <Pricing />

      {/* 为什么升级 */}
      <section className="py-20 px-6 border-t border-[var(--border)]">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-center mb-3 font-display">为什么升级 Pro？</h2>
          <p className="text-[var(--fg-dim)] text-center mb-10">免费版够用，Pro版让你用得更爽</p>

          <div className="space-y-4">
            {whyUpgrade.map((item) => (
              <div key={item.title} className="border border-[var(--border)] rounded-xl p-5 bg-[var(--surface)]">
                <h3 className="text-[15px] font-semibold mb-3 tracking-tight">{item.title}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="text-[13px] text-[var(--fg-dim)] opacity-50">
                    免费版：{item.free}
                  </div>
                  <div className="text-[13px] text-[var(--accent)]">
                    <span className="font-medium">Pro版：</span>{item.pro}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-center mb-10 font-display">常见问题</h2>
          <div className="space-y-2">
            {faqs.map((faq) => (
              <details key={faq.q} className="border border-[var(--border)] rounded-lg group">
                <summary className="cursor-pointer text-[13px] font-medium p-4 list-none flex items-center justify-between">
                  {faq.q}
                  <span className="text-[var(--fg-dim)] text-base transition-transform group-open:rotate-45">+</span>
                </summary>
                <p className="text-[13px] text-[var(--fg-dim)] px-4 pb-4 leading-relaxed">{faq.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

function Pricing() {
  return (
    <section className="py-20 px-6" id="pricing">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-3xl md:text-[2.5rem] font-extrabold tracking-tight text-center mb-3 font-display">免费够用，Pro 更深入</h2>
        <p className="text-[var(--fg-dim)] text-center text-lg mb-12">免费版已包含完整休息提醒功能。Pro 版新增 AI 分析 + 多维度报告。</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 max-w-4xl mx-auto">
          {plans.map((p) => (
            <div
              key={p.name}
              className={`border rounded-xl p-8 h-full bg-[var(--surface)] ${
                p.accent ? 'border-[var(--accent)]' : 'border-[var(--border)]'
              }`}
            >
              {p.badge && (
                <span className="tag mb-4 inline-block">{p.badge}</span>
              )}
              <h3 className="text-xl font-bold mb-1 font-display tracking-tight">{p.name}</h3>
              <p className="text-sm text-[var(--fg-dim)] mb-5">{p.desc}</p>

              <div className="flex items-baseline gap-1.5 mb-7">
                <span className="text-4xl font-bold font-display tracking-tight">{p.price}</span>
                <span className="text-sm text-[var(--fg-dim)]">{p.period}</span>
              </div>

              <ul className="space-y-2.5 mb-8">
                {p.features.map((f: string | { text: string; highlight?: boolean }) => (
                  <li key={typeof f === 'string' ? f : f.text} className="flex items-start gap-2.5 text-[13px] text-[var(--fg-dim)]">
                    <span className="mt-0.5 text-[var(--accent)]">✓</span>
                    <span className={typeof f === 'object' && f.highlight ? 'text-[var(--fg)] font-medium' : ''}>{typeof f === 'string' ? f : f.text}</span>
                  </li>
                ))}
              </ul>

              <a
                href={p.href}
                className={`block text-center py-3 text-sm font-semibold tracking-tight ${
                  p.accent ? 'bg-[var(--accent)] text-[var(--bg)] hover:bg-[var(--accent-bright)] transition-colors' : 'border border-[var(--border)] text-[var(--fg)] hover:border-[var(--accent)] hover:text-[var(--accent)] transition-colors'
                }`}
              >
                {p.cta}
              </a>
            </div>
          ))}
        </div>

        <div className="text-center mt-8 text-[13px] text-[var(--fg-dim)]">
          免费版永久免费 · Pro 19.9元/月，随时取消
        </div>
      </div>
    </section>
  );
}
