import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "隐私政策 — 精力管理 Chrome 扩展",
  description: "「精力管理」Chrome 扩展的隐私政策，说明数据收集、使用、共享方式。所有学习数据默认存储在浏览器本地。",
};

export default function PrivacyChromePage() {
  return (
    <main className="flex-1">
      <div className="max-w-3xl mx-auto px-6 py-20 animate-[fadeInUp_0.5s_ease-out]">
        <div className="docs-card p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-2 font-display">
            隐私政策 — 精力管理 Chrome 扩展
          </h1>
          <p className="text-sm text-[var(--fg-dim)] mb-8">
            生效日期：2026 年 7 月 13 日 · 开发者：kuangketongxue
          </p>

          <div className="space-y-8 text-[var(--fg)] leading-relaxed">
            <section>
              <h2 className="text-xl font-bold mb-3">1. 概述</h2>
              <p className="text-[var(--fg-dim)]">
                「精力管理」Chrome 扩展（以下简称"本扩展"）是一款帮助用户管理学习节奏、定时休息、护眼的工具。
                本扩展遵循<strong>数据最小化</strong>原则，尽可能在本地完成所有功能。
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">2. 本地存储（不经过服务器）</h2>
              <p className="text-[var(--fg-dim)] mb-3">
                本扩展通过 Chrome 的 <code className="bg-[var(--surface)] px-1.5 py-0.5 rounded text-xs font-mono text-[var(--accent)]">chrome.storage.local</code> API 在浏览器本地存储以下数据：
              </p>
              <div className="space-y-2">
                {[
                  ["学习状态（计时器状态、轮次、学习/休息时长）", "驱动计时器显示和状态恢复"],
                  ["复盘记录（每轮评分、学科、标签、时间）", "生成趋势统计和成就系统"],
                  ["用户设置（学习/休息时长、护眼间隔、主题、通知开关）", "个性化体验"],
                  ["成就解锁记录", "展示成就进度"],
                  ["连续打卡天数", "展示连续打卡火焰"],
                ].map(([name, desc]) => (
                  <div key={name} className="flex gap-3 items-start">
                    <span className="text-[var(--accent)] mt-0.5">•</span>
                    <div>
                      <span className="font-medium text-sm">{name}</span>
                      <span className="text-[var(--fg-dim)] text-sm"> — {desc}</span>
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-[var(--fg-dim)] text-sm mt-3">
                <strong className="text-[var(--fg)]">这些数据全部存储在你的浏览器本地，不会自动上传到任何服务器。</strong>
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">3. 可选的数据共享功能</h2>
              <p className="text-[var(--fg-dim)] mb-4">
                以下功能仅在用户<strong>主动配置并触发</strong>时才会共享数据，每一项都是可选的：
              </p>

              <div className="space-y-4">
                {[
                  {
                    title: "3.1 GitHub 备份（可选）",
                    items: [
                      "触发条件：用户在设置页填写 GitHub Token 和仓库名，点击\"立即备份\"",
                      "共享内容：复盘记录、设置等本地数据",
                      "共享对象：用户指定的 GitHub 仓库（通过 https://api.github.com）",
                      "GitHub Token 仅存储在浏览器本地",
                    ],
                  },
                  {
                    title: "3.2 邮件周报（可选）",
                    items: [
                      "触发条件：用户填写收件人邮箱并启用\"每周邮件\"",
                      "共享内容：学习统计摘要",
                      "共享对象：通过 Cloudflare Worker 代理发送邮件",
                    ],
                  },
                  {
                    title: "3.3 AI 学习报告（可选）",
                    items: [
                      "触发条件：用户在\"AI 报告\"页面点击\"生成\"",
                      "共享内容：近 7 天学习统计（轮次、评分）",
                      "共享对象：通过 Cloudflare Worker 代理调用 AI 模型",
                      "AI 报告仅展示在浏览器内，不会被存储",
                    ],
                  },
                  {
                    title: "3.4 B 站链接（可选）",
                    items: [
                      "触发条件：用户配置收藏夹/护眼视频 URL",
                      "无数据传输，仅在新标签页打开 URL",
                      "行为等同于手动在浏览器地址栏输入",
                    ],
                  },
                ].map(({ title, items }) => (
                  <div key={title} className="bg-[var(--surface)] rounded-lg p-5">
                    <h3 className="font-semibold mb-2">{title}</h3>
                    <ul className="space-y-1">
                      {items.map((item) => (
                        <li key={item} className="text-sm text-[var(--fg-dim)] flex gap-2">
                          <span className="text-[var(--accent)]">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">4. 本扩展不收集的信息</h2>
              <div className="space-y-2 text-[var(--fg-dim)]">
                {[
                  "姓名、电话号码等个人身份信息",
                  "浏览历史或网页内容",
                  "位置信息",
                  "Cookie 或网站登录凭证",
                  "未明确告知用户的任何数据",
                ].map((item) => (
                  <p key={item} className="flex gap-2 items-start">
                    <span className="text-[var(--accent)]">—</span>
                    <span>{item}。</span>
                  </p>
                ))}
              </div>
              <p className="mt-3 font-medium">
                没有账号体系、没有跟踪脚本、没有遥测、没有广告。
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">5. 开源与审计</h2>
              <p className="text-[var(--fg-dim)]">
                本项目以 MIT 协议开源，托管在 GitHub：
                <a
                  href="https://github.com/kuangketongxue/library-remind"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[var(--accent)] hover:underline ml-1"
                >
                  github.com/kuangketongxue/library-remind
                </a>
                。任何人都可以审查代码验证隐私声明的真实性。
                Chrome 扩展代码包含在开源仓库的 <code className="bg-[var(--surface)] px-1.5 py-0.5 rounded text-xs font-mono text-[var(--accent)]">chrome-extension/</code> 目录中。
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">6. 数据存储与安全</h2>
              <ul className="space-y-2 text-[var(--fg-dim)]">
                <li>• 本地数据受浏览器沙箱保护，其他扩展和网页无法访问</li>
                <li>• 可选的外部通信（GitHub API、Cloudflare Worker）全部通过 HTTPS 加密传输</li>
                <li>• 开发者无法访问你本地存储的数据</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">7. 数据删除</h2>
              <ul className="space-y-2 text-[var(--fg-dim)]">
                <li>• <strong className="text-[var(--fg)]">删除今日数据</strong>：设置页 → "重置今日"</li>
                <li>• <strong className="text-[var(--fg)]">删除全部数据</strong>：设置页 → "清除全部"（不可恢复）</li>
                <li>• <strong className="text-[var(--fg)]">删除 GitHub 备份</strong>：登录仓库手动删除 <code className="bg-[var(--surface)] px-1 rounded text-xs font-mono">chrome-ext-data/</code> 目录</li>
                <li>• <strong className="text-[var(--fg)]">删除扩展</strong>：chrome://extensions → 移除扩展</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">8. 未成年人保护</h2>
              <p className="text-[var(--fg-dim)]">
                本扩展面向学习人群（包括未成年人），不主动收集个人身份信息。
                监护人如认为未成年人在未经同意的情况下使用了可选共享功能，请联系删除相关数据。
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">9. 隐私政策变更</h2>
              <p className="text-[var(--fg-dim)]">
                本隐私政策可能不时更新。更新后的版本将在本页发布并更新"生效日期"。
                重大变更将通过扩展更新通知用户。
              </p>
            </section>

            <section className="border-t border-[var(--border)] pt-6">
              <h2 className="text-xl font-bold mb-3">10. 联系方式</h2>
              <div className="space-y-2 text-[var(--fg-dim)]">
                <p>
                  • <strong className="text-[var(--fg)]">邮箱</strong>：
                  <a href="mailto:kuangketongxue@gmail.com" className="text-[var(--accent)] hover:underline">
                    kuangketongxue@gmail.com
                  </a>
                </p>
                <p>
                  • <strong className="text-[var(--fg)]">GitHub Issues</strong>：
                  <a
                    href="https://github.com/kuangketongxue/library-remind/issues"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[var(--accent)] hover:underline"
                  >
                    github.com/kuangketongxue/library-remind/issues
                  </a>
                </p>
              </div>
            </section>

            <p className="text-xs text-[var(--fg-muted)] pt-4">
              本文件托管于{" "}
              <a href="https://crazy-rest-reminder.pages.dev" target="_blank" rel="noopener noreferrer" className="text-[var(--accent)] hover:underline">
                crazy-rest-reminder.pages.dev
              </a>
              ，Chrome Web Store 上架时在开发者后台填入{" "}
              <code className="bg-[var(--surface)] px-1 rounded text-xs font-mono">https://crazy-rest-reminder.pages.dev/privacy-chrome</code>。
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
