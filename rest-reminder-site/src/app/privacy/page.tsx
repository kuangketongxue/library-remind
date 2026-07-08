"use client";

import DocsNav from "@/components/DocsNav";
import { useI18n } from "@/lib/i18n";

export default function PrivacyPage() {
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
            <span className="text-[var(--fg)]">{t("privacy.title")}</span>
          </nav>

          <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">{t("privacy.title")}</h1>
          <p className="text-[var(--fg-dim)] mb-10">{t("privacy.subtitle")}</p>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("privacy.section_storage")}</h2>
            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">完全本地存储</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  Rest Reminder 的所有用户数据（学习记录、复盘评分、打卡数据、设置偏好等）均以 JSON 文件形式存储在程序所在目录。数据不经过任何云端服务器，不通过网络传输到第三方。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">无账号体系</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  程序不需要注册、登录或提供任何个人信息。没有用户账号、没有手机号、没有邮箱收集。安装即用，卸载即清。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">无数据上传</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  除用户主动配置的 AI API 调用（仅发送学习统计数据用于生成分析报告）外，程序不会自动上传任何数据。AI 调用内容仅限于脱敏后的学习统计摘要，不包含个人信息。
                </p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("privacy.section_files")}</h2>
            <div className="space-y-3">
              <div className="flex gap-3">
                <code className="bg-[var(--surface)] px-2 py-1 rounded text-xs font-mono text-[var(--accent)] shrink-0">.daily_log.json</code>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">每日学习时长、轮次、休息时长等统计数据</p>
              </div>
              <div className="flex gap-3">
                <code className="bg-[var(--surface)] px-2 py-1 rounded text-xs font-mono text-[var(--accent)] shrink-0">.review_log.json</code>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">每轮复盘的学科、标签、评分记录</p>
              </div>
              <div className="flex gap-3">
                <code className="bg-[var(--surface)] px-2 py-1 rounded text-xs font-mono text-[var(--accent)] shrink-0">.streak.json</code>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">连续打卡天数和最佳记录</p>
              </div>
              <div className="flex gap-3">
                <code className="bg-[var(--surface)] px-2 py-1 rounded text-xs font-mono text-[var(--accent)] shrink-0">.settings.json</code>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">用户设置偏好（含加密存储的 API Key）</p>
              </div>
              <div className="flex gap-3">
                <code className="bg-[var(--surface)] px-2 py-1 rounded text-xs font-mono text-[var(--accent)] shrink-0">.app_state.json</code>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">程序运行状态（计时器、当前轮次等）</p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("privacy.section_audit")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                Rest Reminder 采用 MIT 开源协议，完整源代码托管在 GitHub。任何人都可以审查代码，验证隐私声明的真实性。不存在后门、遥测或隐藏的数据收集逻辑。
              </p>
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                源码仓库：<a href="https://github.com/kuangketongxue/library-remind" target="_blank" rel="noopener noreferrer" className="text-[var(--accent)] hover:underline">github.com/kuangketongxue/library-remind</a>
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("privacy.section_ai")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                AI 学习分析功能需要用户自行配置 API Key。当用户主动触发 AI 报告时，程序会将脱敏后的学习统计数据发送到用户配置的 API 端点。发送内容仅包含：
              </p>
              <ul className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3 space-y-1 list-disc list-inside">
                <li>学习时长统计（小时/轮次）</li>
                <li>复盘评分汇总（平均分、学科分布）</li>
                <li>打卡和连续天数</li>
              </ul>
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                不发送任何可识别个人身份的信息。API Key 使用 XOR + 机器盐值加密存储在本地，不上传。
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4 font-display">{t("privacy.section_third")}</h2>
            <div className="space-y-3">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">Bilibili（B 站）</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  休息时自动打开浏览器访问 B 站收藏夹视频。此操作等同于用户手动在浏览器中输入 URL，不涉及任何数据传输。
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">飞书日程</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  飞书日程为可选功能。启用后通过 lark-cli 读取日程数据，日程信息由飞书 API 返回，仅在本地显示，不缓存到持久化文件。
                </p>
              </div>
            </div>
          </section>

          <section className="mb-16">
            <h2 className="text-xl font-bold mb-4 font-display">{t("privacy.section_delete")}</h2>
            <div className="docs-card">
              <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                删除程序目录即可彻底清除所有数据。如需保留学习记录，建议在卸载前备份以 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">.</code> 开头的 JSON 文件。程序不提供远程数据删除功能，因为不存在远程数据。
              </p>
            </div>
          </section>

          <nav className="border-t border-[var(--border)] pt-8 mt-16 flex flex-col sm:flex-row justify-between gap-4">
            <a href="/docs" className="group flex items-center gap-3 text-sm">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <div>
                <p className="text-[var(--fg-muted)] text-xs">上一页</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">文档</p>
              </div>
            </a>
            <a href="/terms" className="group flex items-center gap-3 text-sm sm:flex-row-reverse">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <div className="sm:text-right">
                <p className="text-[var(--fg-muted)] text-xs">下一页</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">用户协议</p>
              </div>
            </a>
          </nav>
        </div>
      </div>
    </main>
  );
}
