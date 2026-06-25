"use client";

import { motion } from "framer-motion";

const benefits = [
  {
    icon: "📢",
    title: "GitHub README 广告位",
    desc: "中、日、英三语展示，覆盖 GitHub 上的中外开发者。",
  },
  {
    icon: "⚡",
    title: "应用内预设接入",
    desc: "获得高亮推荐，用户从您站点复制 Key 即可一键导入，显著降低配置门槛。",
  },
  {
    icon: "🌐",
    title: "官网赞助商页面展示",
    desc: "在 crazy-rest-reminder.pages.dev 赞助商页面获得长期独立展示，带去精准开发者流量。",
  },
  {
    icon: "🔧",
    title: "优先技术支持",
    desc: "专属对接通道，第一时间协助数据调整、参数适配等技术需求。",
  },
];

const sponsors = [
  { name: "Kimi", desc: "Kimi K2.6 — SOTA coding | Agent swarm | Long-horizon execution" },
  { name: "PackyCode", desc: "稳定高效的 API 中转服务" },
  { name: "AIGoCode", desc: "一站式 AI 编程平台" },
  { name: "胜算云", desc: "工业级 AI 任务并行执行平台" },
  { name: "AICodeMirror", desc: "官方高稳命中中转服务" },
  { name: "PatewayAI", desc: "官方直连高品质 API 中转" },
  { name: "火山方舟", desc: "字节自研全模态大模型平台" },
  { name: "硅基流动", desc: "高性能多模态 AI 基础设施" },
  { name: "Cubence", desc: "可靠高效的 API 中继" },
  { name: "DMXAPI", desc: "一个 Key 用全球大模型" },
  { name: "优云智算", desc: "UCloud 旗下 AI 云平台" },
  { name: "CrazyRouter", desc: "高性能 AI API 聚合平台" },
  { name: "Right Code", desc: "按量 / 包月双模式中转" },
  { name: "SSSAICode", desc: "稳定平价的 Claude / Code..." },
  { name: "米醋 API", desc: "试错零成本的中转服务" },
  { name: "CTok.ai", desc: "一站式 AI 编程工具服务" },
  { name: "Claude API", desc: "官方渠道直供，零降智赠送" },
];

const fade = (delay = 0) => ({
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] as const },
});

export default function Sponsor() {
  return (
    <section className="py-24 px-6" id="sponsor">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div {...fade(0)} className="text-center mb-16">
          <p className="text-[var(--accent)] text-sm font-medium mb-4 tracking-wide">❤️ 开源 · 社区驱动</p>
          <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-5 font-display">
            感谢每一位支持者
          </h2>
          <p className="text-[var(--fg-dim)] text-lg max-w-2xl mx-auto leading-relaxed">
            Rest Reminder 是一个面向学习者的开源项目，由社区与赞助商共同支撑。我们将每一份支持都视为让项目走得更远的力量。
          </p>
        </motion.div>

        {/* Flagship sponsors — core AI services */}
        <motion.div {...fade(0.1)} className="text-center mb-16">
          <h3 className="text-2xl md:text-3xl font-bold mb-3 font-display">核心 AI 服务商</h3>
          <p className="text-[var(--fg-dim)] mb-10">Rest Reminder 的 AI 能力由以下团队提供底层支持</p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {/* LongCat */}
            <div className="card p-6 text-left group">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-[var(--surface-raised)] flex items-center justify-center text-xl font-bold text-[var(--accent)] group-hover:bg-[var(--accent-soft)] transition-colors">
                  🐱
                </div>
                <div>
                  <h4 className="text-sm font-bold">LongCat</h4>
                  <p className="text-[10px] text-[var(--fg-dim)]">美团 · 图像生成</p>
                </div>
              </div>
              <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                美团旗下图像生成模型，6B 参数，中文理解与文字渲染表现亮眼，为项目提供视觉内容生成能力。
              </p>
              <a href="https://huggingface.co/meituan-longcat" target="_blank" rel="noopener noreferrer" className="text-[11px] text-[var(--accent)] hover:underline mt-3 inline-block">HuggingFace →</a>
            </div>

            {/* StepFun */}
            <div className="card p-6 text-left group">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-[var(--surface-raised)] flex items-center justify-center text-xl font-bold text-[var(--accent)] group-hover:bg-[var(--accent-soft)] transition-colors">
                  ⚡
                </div>
                <div>
                  <h4 className="text-sm font-bold">StepFun 阶跃星辰</h4>
                  <p className="text-[10px] text-[var(--fg-dim)]">大模型 · TTS 语音</p>
                </div>
              </div>
              <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                国产大模型先锋，融资超 50 亿。Step 系列模型覆盖文字、视觉、语音，Step Audio 语音合成 API 为休息提醒提供 TTS 播报能力。
              </p>
              <a href="https://platform.stepfun.com" target="_blank" rel="noopener noreferrer" className="text-[11px] text-[var(--accent)] hover:underline mt-3 inline-block">platform.stepfun.com →</a>
            </div>

            {/* SenseNova */}
            <div className="card p-6 text-left group">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-[var(--surface-raised)] flex items-center justify-center text-xl font-bold text-[var(--accent)] group-hover:bg-[var(--accent-soft)] transition-colors">
                  🧠
                </div>
                <div>
                  <h4 className="text-sm font-bold">SenseNova 商汤</h4>
                  <p className="text-[10px] text-[var(--fg-dim)]">多模态大模型 · API</p>
                </div>
              </div>
              <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                商汤科技旗舰大模型平台，SenseNova 系列多模态能力国内领先，为休息提醒的 AI 学习分析报告提供核心推理引擎。
              </p>
              <a href="https://sensenova.cn" target="_blank" rel="noopener noreferrer" className="text-[11px] text-[var(--accent)] hover:underline mt-3 inline-block">sensenova.cn →</a>
            </div>
          </div>
        </motion.div>

        {/* More sponsors */}
        <motion.div {...fade(0.2)}>
          <h3 className="text-2xl font-bold text-center mb-3 font-display">更多赞助商</h3>
          <p className="text-[var(--fg-dim)] text-center mb-10">感谢这些持续支持 Rest Reminder 的伙伴</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto">
            {sponsors.map((s, i) => (
              <motion.div
                key={s.name}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.03, duration: 0.4 }}
                className="card p-5 flex items-center gap-4 group"
              >
                <div className="w-10 h-10 rounded-lg bg-[var(--surface-raised)] flex items-center justify-center text-lg font-bold text-[var(--accent)] group-hover:bg-[var(--accent-soft)] transition-colors">
                  {s.name[0]}
                </div>
                <div className="flex-1 min-w-0">
                  <h5 className="text-sm font-semibold truncate">{s.name}</h5>
                  <p className="text-xs text-[var(--fg-dim)] truncate">{s.desc}</p>
                </div>
                <svg className="w-4 h-4 text-[var(--fg-dim)] opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div {...fade(0.3)} className="text-center mt-16">
          <div className="card p-8 max-w-2xl mx-auto">
            <h4 className="text-lg font-bold mb-2">想要成为赞助商？</h4>
            <p className="text-sm text-[var(--fg-dim)] mb-5">
              无论是 API 服务、工具产品还是其他合作，欢迎联系我们一起让 Rest Reminder 更好。
            </p>
            <a
              href="mailto:support@crazy-rest-reminder.pages.dev?subject=Sponsorship Inquiry - Rest Reminder"
              className="btn-primary inline-flex items-center gap-2 px-6 py-3 text-sm"
            >
              📧 联系合作
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
