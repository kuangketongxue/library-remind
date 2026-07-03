"use client";

import { useState } from "react";

const faqs = [
  {
    q: "AI 分析具体看什么？",
    a: "AI 会读取你的学习时长、打卡记录、自评分数等数据，自动生成日报/周报/月报/季报/年报五级报告。每份报告包含数据分析、趋势判断和个性化改进建议，帮你持续优化学习策略。未配置 API Key 时自动使用本地数据摘要。"
  },
  {
    q: "需要联网才能用吗？",
    a: "核心功能（休息提醒、护眼、学习追踪、趋势分析）完全离线运行。AI 学习分析需要联网调用 SenseNova API，其余功能全部本地可用，数据不离开你的电脑。"
  },
  {
    q: "支持哪些系统？",
    a: "目前支持 Windows 10/11（基于 PyQt5 和 Windows 注册表自启）。macOS 和 Linux 版本正在规划中。"
  },
  {
    q: "安装需要 Python 吗？",
    a: "不用。下载 exe 双击直接运行，无需安装 Python。如果从源码运行，需要 Python 3.8+ 和 PyQt5。"
  },
  {
    q: "数据会丢失吗？",
    a: "所有数据存储在本地 JSON 文件（.daily_log.json、.review_log.json、.streak.json 等），重启电脑不丢失。重装系统前建议备份这些文件。"
  },
  {
    q: "完全免费吗？",
    a: "是的。MIT 开源协议，所有功能直接可用，无隐藏收费、无订阅、无限制。AI 分析基于免费 API，无需付费。"
  },
  {
    q: "连续打卡中断了怎么办？",
    a: "连续打卡基于每日学习时长判断（满 4 小时算达标）。如果某天未达标，连续天数归零，但最佳记录保留。第二天达标后重新开始累计。"
  },
  {
    q: "如何配置 AI 报告？",
    a: "在设置页面填入 SenseNova API Key。AI 报告会自动调用 API 生成分析，未配置时降级为本地数据摘要，不会报错。"
  },
  {
    q: "B 站收藏夹怎么设置？",
    a: "默认使用项目内置收藏夹。如需更换，在设置中修改 B 站收藏夹 ID（fid）和用户 ID（mid）。每轮休息后自动打开收藏夹中的视频。"
  },
  {
    q: "浮球可以拖动吗？",
    a: "可以。长按浮球拖动到任意位置，下次启动记住位置。短点击弹出信息面板，显示当前倒计时、学习时长和目标进度。如需隐藏浮球，可在托盘菜单中切换。"
  },
];

function FAQItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div
      className="border border-[var(--border)] rounded-xl overflow-hidden cursor-pointer transition-colors hover:border-[var(--accent)]"
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
