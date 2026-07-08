"use client";

import DocsNav from "@/components/DocsNav";
import { useI18n } from "@/lib/i18n";

export default function TermsPage() {
  const { t } = useI18n();
  return (
    <main className="flex-1">
      <div className="docs-layout">
        <DocsNav />
        <div className="docs-main" style={{ maxWidth: "960px" }}>
          <nav className="flex items-center gap-2 text-xs text-[var(--fg-dim)] mb-6">
            <a href="/" className="hover:text-[var(--fg)] transition-colors">{t("nav.docs")}</a>
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-[var(--fg)]">{t("terms.title")}</span>
          </nav>

          <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">{t("terms.title")}</h1>
          <p className="text-[var(--fg-dim)] mb-10">{t("terms.subtitle")}</p>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("terms.section_license")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                Rest Reminder 基于 <strong>MIT 开源协议</strong>发布。MIT 协议是最宽松的开源协议之一，允许你自由使用、复制、修改、合并、发布、分发、再授权和/或销售本软件的副本。
              </p>
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                唯一的要求是在所有副本或重要部分中保留版权声明和许可声明。详见源码仓库中的 LICENSE 文件。
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("terms.section_disclaimer")}</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">软件按「现状」提供</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  本软件按「现状」和「现有」基础提供，不附带任何明示或暗示的保证，包括但不限于对适销性、特定用途适用性和非侵权的暗示保证。在任何情况下，作者或版权持有人均不对任何索赔、损害或其他责任负责。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">健康提醒非医疗建议</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  Rest Reminder 提供的休息提醒、护眼提醒（20-20-20 法则）等功能仅供参考，不构成医疗或健康建议。如果你的眼睛或身体出现不适，请及时就医，遵循专业医生的指导。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">学习效果声明</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  程序提供的 AI 学习分析报告基于算法生成，仅供参考和启发，不保证学习效果的提升。实际学习成果取决于使用者自身的学习方法和努力程度。
                </p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("terms.section_limits")}</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">平台限制</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  Rest Reminder 目前仅支持 Windows 10/11 操作系统。基于 PyQt5 GUI 框架和 Windows API（ctypes）开发，不支持 macOS 和 Linux。强行在其他平台运行可能导致功能异常。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">Python 版本要求</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  源码运行需要 Python 3.14 或更高版本。项目内嵌的 vendor 目录中的二进制文件按 Python 3.14 ABI 编译，使用其他版本会导致 ImportError。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">AI 服务需用户自行配置</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  AI 学习分析功能需要用户自行获取并配置第三方 AI 服务的 API Key。程序不提供内置 API Key，不承担第三方 API 服务的可用性、费用和数据安全责任。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">禁止行为</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li>将本软件用于非法用途</li>
                  <li>移除或修改版权声明和许可声明后分发</li>
                  <li>声称本软件的原始作者身份（除非你是原始作者）</li>
                  <li>对本软件进行逆向工程并声称是原创作品</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("terms.section_changes")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                开发者保留随时修改、更新或终止本软件的权利，无需事先通知。MIT 协议保证你已获取的版本可以永久使用和修改。建议通过 GitHub 关注更新。
              </p>
            </div>
          </section>

          <section className="mb-16">
            <h2 className="text-xl font-bold mb-4 font-display">{t("terms.section_contact")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                如对本协议有任何疑问，请通过 GitHub Issues 提交，或发送邮件至 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">kuangketongxue@gmail.com</code>。
              </p>
            </div>
          </section>

          <nav className="border-t border-[var(--border)] pt-8 mt-16 flex flex-col sm:flex-row justify-between gap-4">
            <a href="/privacy" className="group flex items-center gap-3 text-sm">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <div>
                <p className="text-[var(--fg-muted)] text-xs">上一页</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">隐私政策</p>
              </div>
            </a>
            <a href="/rules" className="group flex items-center gap-3 text-sm sm:flex-row-reverse">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <div className="sm:text-right">
                <p className="text-[var(--fg-muted)] text-xs">下一页</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">管理规则和公约</p>
              </div>
            </a>
          </nav>
        </div>
      </div>
    </main>
  );
}
