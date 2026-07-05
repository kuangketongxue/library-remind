"use client";

import DocsNav from "@/components/DocsNav";

export default function RulesPage() {
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
            <span className="text-[var(--fg)]">管理规则和公约</span>
          </nav>

          <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">管理规则和公约</h1>
          <p className="text-[var(--fg-dim)] mb-10">最后更新：2026 年 7 月 4 日</p>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">社区行为准则</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">尊重与友善</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  在 GitHub Issues、Discussions 和其他社区交流中，保持尊重和友善的态度。不使用攻击性语言，不对他人进行人身攻击。建设性的批评和反馈是受欢迎的，但请保持客观和专业。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">保持专注</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  Issue 和讨论应与 Rest Reminder 项目直接相关。技术讨论、功能建议、Bug 报告都是合适的主题。偏离主题的内容可能会被关闭或移除。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">开源协作精神</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  本项目是 MIT 开源的社区项目。欢迎任何人参与贡献，无论是代码、文档、翻译还是设计。贡献者应遵循本公约，维护一个包容、开放的协作环境。
                </p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">Issue 规范</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">提交前检查</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">提交 Issue 前，请确认：</p>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li>已搜索现有 Issues，确认问题未被报告过</li>
                  <li>已阅读文档和常见问题，确认不是已知问题</li>
                  <li>使用的是最新版本（GitHub Releases 页面查看）</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">Bug 报告格式</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">Bug 报告应包含以下信息：</p>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li><strong>版本号</strong> — 程序主界面「关于」页面显示的版本</li>
                  <li><strong>操作系统</strong> — Windows 10/11，是否为最新更新</li>
                  <li><strong>复现步骤</strong> — 导致问题的具体操作序列</li>
                  <li><strong>预期行为</strong> — 你期望看到的结果</li>
                  <li><strong>实际行为</strong> — 实际发生的结果</li>
                  <li><strong>crash.log</strong> — 如有崩溃日志，请附上完整内容</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">功能建议</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  功能建议应清楚描述你希望的功能、使用场景和预期效果。越具体越好。例如，与其说「加个番茄钟功能」，不如描述你理想中的计时流程和交互方式。
                </p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">Pull Request 规范</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">提交前</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li>Fork 仓库，在独立分支上开发，不要直接修改 main</li>
                  <li>确保代码通过 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">py_compile</code> 语法检查</li>
                  <li>如修改了 UI 逻辑，说明测试方法和验证结果</li>
                  <li>遵循现有代码风格（参考 CLAUDE.md 中的规范）</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">PR 描述</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">PR 描述应包含：</p>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li>改动目的和背景</li>
                  <li>改动内容的简要说明</li>
                  <li>关联的 Issue（如有）</li>
                  <li>测试验证方式</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">代码审查</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  所有 PR 都需要经过代码审查才能合并。审查关注点包括：代码质量、边界情况处理、与现有架构的一致性、以及对用户体验的影响。审查意见是协作的一部分，请以开放态度对待。
                </p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">违规处理</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                对于严重违反本公约的行为（恶意骚扰、垃圾信息、恶意 PR 等），维护者有权关闭相关 Issue/PR，必要时封禁相关账户。所有处理决定由维护者酌情做出，旨在维护社区的健康发展。
              </p>
            </div>
          </section>

          <section className="mb-16">
            <h2 className="text-xl font-bold mb-4 font-display">版本号约定</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">项目采用语义化版本号（Semantic Versioning）：</p>
              <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                <li><strong>主版本号（X.0.0）</strong> — 架构重大变更、不向后兼容的修改</li>
                <li><strong>次版本号（0.X.0）</strong> — 新功能、功能增强，向后兼容</li>
                <li><strong>修订号（0.0.X）</strong> — Bug 修复、小改进</li>
              </ul>
            </div>
          </section>

          <nav className="border-t border-[var(--border)] pt-8 mt-16 flex flex-col sm:flex-row justify-between gap-4">
            <a href="/terms" className="group flex items-center gap-3 text-sm">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <div>
                <p className="text-[var(--fg-muted)] text-xs">上一页</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">用户协议</p>
              </div>
            </a>
            <a href="/pricing" className="group flex items-center gap-3 text-sm sm:flex-row-reverse">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <div className="sm:text-right">
                <p className="text-[var(--fg-muted)] text-xs">下一页</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">定价计费</p>
              </div>
            </a>
          </nav>
        </div>
      </div>
    </main>
  );
}
