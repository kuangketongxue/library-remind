"use client";

import DocsNav from "@/components/DocsNav";

export default function DocsPage() {
  return (
    <main className="flex-1">
      <div className="max-w-6xl mx-auto flex">
        {/* 左侧导航 */}
        <DocsNav />

        {/* 右侧内容 */}
        <div className="flex-1 min-w-0 px-6 py-12">
          <div className="max-w-3xl">
            <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">文档</h1>
            <p className="text-[var(--fg-dim)] mb-10">Rest Reminder 使用指南、更新日志与常见问题。</p>

            {/* 快速开始 */}
            <section className="mb-12">
              <h2 className="text-xl font-bold mb-1 font-display">快速开始</h2>
              <p className="text-[var(--fg-dim)] text-sm mb-4">5 分钟上手 Rest Reminder</p>

              <div className="space-y-6">
                <div>
                  <h3 className="text-base font-semibold mb-2">1. 下载运行</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                    双击 <code className="bg-[var(--surface-raised)] px-1.5 py-0.5 rounded text-xs">_launch.vbs</code> 启动程序，
                    或在命令行运行 <code className="bg-[var(--surface-raised)] px-1.5 py-0.5 rounded text-xs">python rest_reminder.py</code>。
                    首次运行会自动创建数据文件（.daily_log.json 等）。
                  </p>
                </div>

                <div>
                  <h3 className="text-base font-semibold mb-2">2. 设定今日目标</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                    启动后弹出目标对话框，输入今天主要学习内容，选择预计轮次。
                    目标是可选的，随时可以从主界面重新设定。
                  </p>
                </div>

                <div>
                  <h3 className="text-base font-semibold mb-2">3. 开始学习</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                    点击浮球弹出信息面板，按 <code className="bg-[var(--surface-raised)] px-1.5 py-0.5 rounded text-xs">▶ 开始学习</code> 启动 60 分钟倒计时。
                    倒计时结束后自动进入 5 分钟休息，休息结束自动打开 B 站收藏夹。
                  </p>
                </div>

                <div>
                  <h3 className="text-base font-semibold mb-2">4. 复盘与追踪</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                    每小时休息时弹出复盘评分（1-100 分），记录学科和标签。
                    主界面「今日」tab 实时显示学习时长、轮次、连续打卡天数。
                  </p>
                </div>
              </div>
            </section>

            {/* 功能说明 */}
            <section className="mb-12">
              <h2 className="text-xl font-bold mb-1 font-display">功能说明</h2>
              <p className="text-[var(--fg-dim)] text-sm mb-4">核心功能一览</p>

              <div className="space-y-4">
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">⏱ 60 分钟专注循环</h3>
                  <p className="text-[var(--fg-dim)] text-sm">学习 60 分钟 → 5 分钟请辨倒计时（显示金句） → 5 分钟休息 → 自动打开 B 站收藏夹，循环往复。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">👁 20-20-20 护眼提醒</h3>
                  <p className="text-[var(--fg-dim)] text-sm">每 20 分钟弹出轻量浮窗，提醒看 6 米外 20 秒，15 秒自动消失，不打断学习流。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">📊 学习时长追踪</h3>
                  <p className="text-[var(--fg-dim)] text-sm">实时统计学习时长，连续打卡 + 里程碑金句 + 每小时复盘评分，数据持久化到本地。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">📈 趋势分析</h3>
                  <p className="text-[var(--fg-dim)] text-sm">5 标签页趋势图（今日复盘/周趋势/月趋势/季年趋势/时段分析），柱状图 + 热力图双视图，鼠标悬浮查看数值。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">🤖 AI 学习分析</h3>
                  <p className="text-[var(--fg-dim)] text-sm">AI 自动生成日报/周报/月报/季报/年报，分析学习节奏和专注模式。基于 SenseNova API，无需付费。</p>
                </div>
              </div>
            </section>

            {/* 更新日志 */}
            <section className="mb-12">
              <h2 className="text-xl font-bold mb-1 font-display">更新日志</h2>
              <p className="text-[var(--fg-dim)] text-sm mb-6">版本迭代记录</p>

              <div className="space-y-6">
                <div className="border-l-2 border-[var(--accent)] pl-4">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-bold">v5.1.0</span>
                    <span className="text-xs text-[var(--fg-dim)]">2026-06-26</span>
                  </div>
                  <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                    <li>主界面全面实时刷新：学习时长/轮次/休息时长/状态/倒计时每秒更新</li>
                    <li>修复复盘摘要空列表崩溃</li>
                    <li>修复连续打卡恢复逻辑 + 月趋势/季年趋势统计错误</li>
                    <li>删除死代码，移除失效窗口按钮</li>
                  </ul>
                </div>

                <div className="border-l-2 border-[var(--border)] pl-4">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-bold">v5.0.0</span>
                    <span className="text-xs text-[var(--fg-dim)]">2026-06-25</span>
                  </div>
                  <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                    <li>柱状图悬浮提示、复盘学科新增「其他」</li>
                    <li>AI 报告后台线程，趋势分析全面重构</li>
                    <li>修复 AI 报告卡死、tooltip 不显示等 3 个 P0 bug</li>
                  </ul>
                </div>

                <div className="border-l-2 border-[var(--border)] pl-4">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-bold">v4.4.0</span>
                    <span className="text-xs text-[var(--fg-dim)]">2026-06-23</span>
                  </div>
                  <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                    <li>5 标签页主界面（今日/AI报告/趋势/设置/关于）</li>
                    <li>⚡ 浮球独立、20-20-20 护眼浮窗、热力图</li>
                    <li>开源发布：移除 Pro 订阅系统，全部功能免费</li>
                  </ul>
                </div>

                <div className="border-l-2 border-[var(--border)] pl-4">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-bold">v4.3.0</span>
                    <span className="text-xs text-[var(--fg-dim)]">2026-06-21</span>
                  </div>
                  <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                    <li>固定 60 分钟学习 → 5 分钟请辨 → 5 分钟休息</li>
                    <li>每 3 轮护眼视频、复盘在休息期间弹出</li>
                  </ul>
                </div>
              </div>

              <p className="text-[var(--fg-dim)] text-sm mt-6">
                完整更新日志见 <a href="https://github.com/kuangketongxue/library-remind/blob/main/CHANGELOG.md" target="_blank" rel="noopener noreferrer" className="text-[var(--accent)] hover:underline">GitHub CHANGELOG.md</a>
              </p>
            </section>

            {/* 常见问题 */}
            <section className="mb-12">
              <h2 className="text-xl font-bold mb-1 font-display">常见问题</h2>
              <p className="text-[var(--fg-dim)] text-sm mb-6">遇到问题？看看这里有没有答案</p>

              <div className="space-y-4">
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-2">程序启动后只看到浮球，主界面不显示？</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">正常行为。默认静默启动只显示右下角浮球，点击浮球打开主界面。如需启动即显示主窗口，在设置中关闭「静默启动」。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-2">B 站收藏夹没打开？</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">检查设置中的 B 站收藏夹 ID（fid）和用户 ID（mid）是否正确。默认使用项目内置的收藏夹，如需更换请在设置中修改。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-2">AI 报告生成失败？</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">检查设置中是否配置了 SenseNova API Key。也可在「关于」页面的环境检查中诊断依赖安装状态。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-2">数据存在哪里？</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">所有数据存储在程序同目录下的 JSON 文件中（.daily_log.json、.review_log.json、.stats_history.json 等）。卸载程序前建议备份这些文件。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-2">支持 macOS / Linux 吗？</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">目前仅支持 Windows 10/11。macOS 和 Linux 版本正在规划中。</p>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}
