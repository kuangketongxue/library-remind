"use client";

import DocsNav from "@/components/DocsNav";

export default function PricingPage() {
  return (
    <main className="flex-1">
      <div className="docs-layout">
        <DocsNav />
        <div className="docs-main" style={{ maxWidth: "960px" }}>
          <nav className="flex items-center gap-2 text-xs text-[var(--fg-dim)] mb-6">
            <a href="/" className="hover:text-[var(--fg)] transition-colors">首页</a>
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-[var(--fg)]">定价计费</span>
          </nav>

          <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">定价计费</h1>
          <p className="text-[var(--fg-dim)] mb-10">最后更新：2026 年 7 月 4 日</p>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">核心原则：永久免费</h2>
            <div className="docs-card" style={{ borderLeft: "3px solid var(--accent)" }}>
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                Rest Reminder 的所有功能<strong>永久免费</strong>，无订阅、无隐藏收费、无功能限制。从核心的休息提醒到高级的 AI 学习分析，所有功能对所有用户平等开放。
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">免费功能一览</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">核心功能</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1.5">
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 60 分钟专注循环</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 5 分钟请辨倒计时</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 5 分钟休息</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> B 站收藏夹自动打开</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 20-20-20 护眼提醒</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 每 3 轮护眼视频</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">学习追踪</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1.5">
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 学习时长累计</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 复盘评分系统</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 连续打卡 + 里程碑</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 趋势分析（周/月/季/年）</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 7x24 学习热力图</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 成就/徽章系统（17 个）</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">AI 功能</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1.5">
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> AI 学习分析报告</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 日报 / 周报 / 月报 / 季报 / 年报</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 多 AI 提供商切换</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 本地数据降级报告（无 Key 可用）</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> TTS 语音播报</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">集成与扩展</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1.5">
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 飞书日程集成</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 环境白噪音</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 主题切换（深色/浅色）</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 全局快捷键</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> 电池监控</li>
                  <li className="flex gap-2"><span className="text-[var(--accent)]">&#10003;</span> GitHub 自动备份</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">费用说明</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">Rest Reminder 本身</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  <strong>完全免费</strong>。下载、安装、使用不收取任何费用。没有免费试用期，没有基础版/高级版区分，所有功能开箱即用。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">AI API 费用</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  AI 学习分析功能使用用户自行配置的第三方 API（如 SenseNova、OpenAI 兼容接口等）。API 调用费用由第三方服务商收取，与 Rest Reminder 项目无关。项目内置了免费的 Cloudflare 代理 Key，用户无需自行购买 API Key 即可使用基础 AI 报告功能。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">无隐藏收费</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  没有「后续收费」、没有「增值服务」、没有「内购」。项目由开发者个人维护，经费来源于个人和赞助，不向用户收取任何费用。
                </p>
              </div>
            </div>
          </section>

          <section className="mb-16">
            <h2 className="text-xl font-bold mb-4 font-display">常见疑问</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">为什么免费？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  这是一个学生个人项目，最初是为了解决自己的学习效率问题而开发的。开源免费分享给更多人使用，让每个人都受益于科学的学习休息节奏。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">以后会收费吗？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  不会。MIT 开源协议保证了任何人都可以永久免费使用。即使原始开发者停止维护，你仍然可以自由使用、修改和分发。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">如何支持项目？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  如果你觉得 Rest Reminder 帮助了你，可以通过以下方式支持项目：
                </p>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed mt-2 space-y-1 list-disc list-inside">
                  <li>在 GitHub 上给项目点 Star</li>
                  <li>提交 Issue 反馈问题或建议</li>
                  <li>提交 PR 贡献代码或文档</li>
                  <li>向同学朋友推荐</li>
                  <li>赞助支持开发者（详见赞助页）</li>
                </ul>
              </div>
            </div>
          </section>

          <nav className="border-t border-[var(--border)] pt-8 mt-16 flex flex-col sm:flex-row justify-between gap-4">
            <a href="/rules" className="group flex items-center gap-3 text-sm">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <div>
                <p className="text-[var(--fg-muted)] text-xs">上一页</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">管理规则和公约</p>
              </div>
            </a>
            <a href="/docs" className="group flex items-center gap-3 text-sm sm:flex-row-reverse">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <div className="sm:text-right">
                <p className="text-[var(--fg-muted)] text-xs">下一页</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">文档</p>
              </div>
            </a>
          </nav>
        </div>
      </div>
    </main>
  );
}
