"use client";

import { motion } from "framer-motion";

const fade = (delay = 0) => ({
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] as const },
});

const sponsors = [
  { name: "LongCat", desc: "美团旗下图像生成模型，为项目提供视觉内容生成能力", url: "https://longcat.chat/platform/docs/zh/" },
  { name: "StepFun 阶跃星辰", desc: "国产大模型先锋，Step Audio 语音合成 API 为休息提醒提供 TTS 播报能力", url: "https://platform.stepfun.com" },
  { name: "SenseNova 商汤", desc: "多模态大模型平台，为 AI 学习分析报告提供核心推理引擎", url: "https://sensenova.cn" },
  { name: "XiaomiMimo", desc: "技术支持伙伴", url: "https://xiumimo.com" },
  { name: "CC Switch", desc: "AI 编程 CLI 统一管理工具", url: "https://ccswitch.io" },
];

const techSupport = [
  { name: "LongCat", desc: "图像生成" },
  { name: "StepFun", desc: "大模型 / TTS 语音" },
  { name: "SenseNova", desc: "多模态大模型 · API" },
  { name: "XiaomiMimo", desc: "技术支持" },
  { name: "CC Switch", desc: "AI 编程 CLI 管理" },
];

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

        {/* Core sponsors */}
        <motion.div {...fade(0.1)} className="text-center mb-16">
          <h3 className="text-2xl md:text-3xl font-bold mb-3 font-display">核心赞助商</h3>
          <p className="text-[var(--fg-dim)] mb-10">Rest Reminder 的 AI 能力由以下团队提供底层支持</p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {sponsors.map((s) => (
              <a key={s.name} href={s.url} target="_blank" rel="noopener noreferrer" className="card p-6 text-left group">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-[var(--surface-raised)] flex items-center justify-center text-xl font-bold text-[var(--accent)] group-hover:bg-[var(--accent-soft)] transition-colors">
                    {s.name[0]}
                  </div>
                  <h4 className="text-sm font-bold">{s.name}</h4>
                </div>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{s.desc}</p>
              </a>
            ))}
          </div>
        </motion.div>

        {/* Technical support */}
        <motion.div {...fade(0.15)} className="text-center mb-16">
          <h3 className="text-2xl md:text-3xl font-bold mb-3 font-display">技术支持</h3>
          <p className="text-[var(--fg-dim)] mb-10">感谢以下伙伴在技术层面的支持</p>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 max-w-3xl mx-auto">
            {techSupport.map((s) => (
              <div key={s.name} className="card p-4 text-center">
                <h5 className="text-sm font-semibold mb-1">{s.name}</h5>
                <p className="text-[10px] text-[var(--fg-dim)]">{s.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Contact CTA */}
        <motion.div {...fade(0.2)} className="text-center mt-16">
          <div className="card p-8 max-w-2xl mx-auto">
            <h4 className="text-lg font-bold mb-2">商务合作 / 赞助</h4>
            <p className="text-sm text-[var(--fg-dim)] mb-4">
              无论是 API 服务、工具产品还是其他合作，欢迎联系。
            </p>
            <a
              href="mailto:kuangketongxue@gmail.com"
              className="text-[var(--accent)] hover:underline text-sm font-mono"
            >
              kuangketongxue@gmail.com
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
