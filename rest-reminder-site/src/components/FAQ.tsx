"use client";

import { useState } from "react";

const faqs = [
  { q: "免费版和Pro版有什么区别？", a: "免费版包含全部休息提醒、护眼、学习追踪功能。Pro 版在此基础上提供 AI 学习分析 + 日报/周报/月报/季报/年报——自动分析你的学习数据，生成多维度报告和个性化建议。" },
  { q: "AI 分析具体看什么？", a: "AI 会读取你的学习时长、打卡记录、自评分数等数据，生成日报/周报/月报/季报/年报五级报告。每份报告包含数据分析、趋势判断和个性化改进建议，帮你持续优化学习策略。" },
  { q: "需要联网才能用吗？", a: "免费版完全离线运行。Pro 版 AI 分析需要联网调用 API，其余功能离线可用。" },
  { q: "Pro 版如何支付？", a: "19.9元/月，通过 Supabase 验证订阅状态。支持随时取消。" },
  { q: "支持哪些系统？", a: "目前支持 Windows 10/11。macOS 和 Linux 版本正在开发中。" },
  { q: "安装需要Python吗？", a: "不用。下载 exe 双击直接运行，无需安装 Python。" },
  { q: "数据会丢失吗？", a: "数据存储在本地 JSON 文件，重启电脑不丢失。重装系统前备份相关文件即可。" },
];

function FAQItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div
      className="border border-[var(--border)] rounded-lg overflow-hidden cursor-pointer transition-colors hover:border-[var(--accent)]"
      onClick={() => setOpen(!open)}
    >
      <div className="flex items-center justify-between p-4">
        <span className="text-[13px] font-medium">{q}</span>
        <span className="text-[var(--fg-dim)] text-base transition-transform duration-200" style={{ transform: open ? "rotate(45deg)" : "rotate(0)" }}>
          +
        </span>
      </div>
      <div className="grid transition-all duration-200" style={{ gridTemplateRows: open ? '1fr' : '0fr' }}>
        <div className="overflow-hidden">
          <p className="px-4 pb-4 text-[13px] text-[var(--fg-dim)] leading-relaxed">{a}</p>
        </div>
      </div>
    </div>
  );
}

export default function FAQ() {
  return (
    <section className="py-20 px-6" id="faq">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-center mb-3 font-display">常见问题</h2>
        <p className="text-[var(--fg-dim)] text-center mb-10">有疑问？这里可能有答案。</p>

        <div className="space-y-2">
          {faqs.map((faq) => (
            <FAQItem key={faq.q} q={faq.q} a={faq.a} />
          ))}
        </div>
      </div>
    </section>
  );
}
