"use client";

import DocsNav from "@/components/DocsNav";
import DocsTOC from "@/components/DocsTOC";

export default function DocsPage() {
  return (
    <main className="flex-1">
      <div className="docs-layout">
        {/* 左侧导航 */}
        <DocsNav />

        {/* 内容区 */}
        <div className="docs-main" style={{ maxWidth: "800px" }}>
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-xs text-[var(--fg-dim)] mb-6">
            <a href="/" className="hover:text-[var(--fg)] transition-colors">首页</a>
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-[var(--fg)]">文档</span>
          </nav>

          {/* 搜索框 */}
          <div className="mb-8" id="搜索">
            <div className="relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--fg-muted)]" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8" /><path strokeLinecap="round" d="M21 21l-4.35-4.35" />
              </svg>
              <input
                id="doc-search-input"
                type="text"
                placeholder="搜索文档…"
                className="w-full pl-10 pr-4 py-2.5 text-sm bg-[var(--surface)] border border-[var(--border)] rounded-lg text-[var(--fg)] placeholder:text-[var(--fg-muted)] focus:outline-none focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] transition-colors"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    const q = (e.target as HTMLInputElement).value.trim().toLowerCase();
                    if (!q) return;
                    const sections = document.querySelectorAll("section[id]");
                    for (const s of sections) {
                      if (s.textContent?.toLowerCase().includes(q)) {
                        s.scrollIntoView({ behavior: "smooth", block: "start" });
                        break;
                      }
                    }
                  }
                }}
              />
              <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-[var(--fg-muted)] bg-[var(--bg)] border border-[var(--border)] rounded px-1.5 py-0.5">Enter</kbd>
            </div>
          </div>

          <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">
            文档
          </h1>
          <p className="text-[var(--fg-dim)] mb-10">
            Rest Reminder 完整使用指南，从快速上手到高级功能。
          </p>

          {/* ── 产品简介 ── */}
          <section className="mb-16" id="简介">
            <h2 className="text-2xl font-bold mb-1 font-display">Rest Reminder 是什么</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">一款免费开源的 Windows 桌面久坐提醒工具</p>

            <div className="docs-card mb-6">
              <p className="text-sm text-[var(--fg)] leading-relaxed mb-3">
                <strong>Rest Reminder</strong> 是一款专为长时间学习/工作设计的桌面护眼助手。它会在你专注 60 分钟后自动提醒你休息，帮你养成科学的用眼习惯，保护视力健康。
              </p>
              <p className="text-sm text-[var(--fg)] leading-relaxed mb-3">
                核心功能包括：<strong>60 分钟专注循环</strong>（学习→倒计时→休息→B 站视频）、<strong>20-20-20 护眼提醒</strong>（每 20 分钟看远处 20 秒）、<strong>学习时长追踪</strong>（连续打卡 + 成就系统）、<strong>AI 学习分析</strong>（日报/周报/月报）。
              </p>
              <p className="text-sm text-[var(--fg-dim)] leading-relaxed">
                48MB 轻量安装，数据完全本地存储，MIT 开源协议，永久免费。
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="docs-card text-center">
                <div className="text-2xl font-bold text-[var(--accent)] mb-1">48MB</div>
                <div className="text-xs text-[var(--fg-dim)]">轻量安装</div>
              </div>
              <div className="docs-card text-center">
                <div className="text-2xl font-bold text-[var(--accent)] mb-1">60min</div>
                <div className="text-xs text-[var(--fg-dim)]">专注循环</div>
              </div>
              <div className="docs-card text-center">
                <div className="text-2xl font-bold text-[var(--accent)] mb-1">17</div>
                <div className="text-xs text-[var(--fg-dim)]">成就徽章</div>
              </div>
              <div className="docs-card text-center">
                <div className="text-2xl font-bold text-[var(--accent)] mb-1">MIT</div>
                <div className="text-xs text-[var(--fg-dim)]">开源协议</div>
              </div>
            </div>
          </section>

          {/* ── 快速开始 ── */}
          <section className="mb-16" id="快速开始">
            <h2 className="text-2xl font-bold mb-1 font-display">快速开始</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">5 分钟上手 Rest Reminder</p>

            <div className="docs-callout mb-6">
              <p className="text-sm font-semibold mb-2">隐私与数据安全</p>
              <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                所有数据仅存储在本地 JSON 文件，不上传任何服务器。无需注册账号，无需登录，MIT 开源可审计。
              </p>
            </div>

            <div className="space-y-8">
              <div id="下载运行">
                <h3 className="text-base font-semibold mb-3 font-display">1. 下载运行</h3>
                <div className="docs-card mb-3">
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-3">
                    双击 _launch.vbs 启动程序。无需安装 Python，无需额外依赖。
                  </p>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                    如果从源码运行，确保已安装依赖：
                  </p>
                  <pre className="bg-[var(--surface)] rounded-lg p-4 mt-3 text-xs font-mono text-[#b5651d] overflow-x-auto">
{`pip install -r requirements.txt
python rest_reminder.py`}
                  </pre>
                </div>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  首次运行会在程序目录创建数据文件（.daily_log.json、.review_log.json 等），用于持久化学习数据。
                </p>
              </div>

              <div id="设定目标">
                <h3 className="text-base font-semibold mb-3 font-display">2. 设定今日目标</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  启动后弹出目标设置对话框。输入今天主要学习内容（如"数学导数+英语阅读"），选择预计完成轮次。目标会显示在浮球信息面板中，提醒你当前进度。
                </p>
                <div className="docs-card mt-3">
                  <p className="text-xs text-[var(--fg-dim)]">
                    <span className="text-[var(--accent)]">提示：</span> 目标是可选的。跳过不影响计时功能，随时可从主界面或浮球面板重新设定。
                  </p>
                </div>
              </div>

              <div id="开始学习">
                <h3 className="text-base font-semibold mb-3 font-display">3. 开始学习</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  程序默认以浮球形式驻留桌面右侧。点击浮球弹出信息面板，按 ▶ 开始学习 启动 60 分钟倒计时。
                </p>
                <div className="docs-card mt-3">
                  <p className="text-sm font-semibold mb-2">计时流程</p>
                  <div className="flex items-center gap-2 text-sm text-[var(--fg-dim)]">
                    <span className="bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-1 rounded-lg font-mono text-xs">60min 学习</span>
                    <span>→</span>
                    <span className="bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-1 rounded-lg font-mono text-xs">5min 请辨</span>
                    <span>→</span>
                    <span className="bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-1 rounded-lg font-mono text-xs">5min 休息</span>
                    <span>→</span>
                    <span className="bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-1 rounded-lg font-mono text-xs">B站视频</span>
                  </div>
                </div>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                  最后 5 分钟弹出请辨浮层，展示随机金句。倒计时结束自动进入休息状态，休息结束后自动打开 B 站收藏夹视频。
                </p>
              </div>

              <div id="复盘追踪">
                <h3 className="text-base font-semibold mb-3 font-display">4. 复盘与追踪</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  每小时学习结束后弹出复盘弹窗，为你提供一个反思和评估学习效果的机会。
                </p>
                <div className="space-y-3 mt-3">
                  <div className="docs-card">
                    <p className="text-sm font-semibold mb-1">📝 复盘评分</p>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                      滑块选择 1-100 分评分，记录学科（语/数/英/物/化/政/其他）和标签（专注/疲劳/收获大/走神/其他）。数据持久化到本地，供趋势分析和 AI 报告使用。
                    </p>
                  </div>
                  <div className="docs-card">
                    <p className="text-sm font-semibold mb-1">🔥 连续打卡</p>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                      每日学习满 4 小时自动打卡。连续打卡到达里程碑（1/3/7/14/30/60/90/365 天）时展示特殊金句奖励。中断后重新开始计数。
                    </p>
                  </div>
                  <div className="docs-card">
                    <p className="text-sm font-semibold mb-1">📊 实时数据</p>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                      「今日」tab 每秒刷新学习时长、当前轮次、休息时长、状态标签。22:00 自动弹出每日学习汇报。
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* ── 界面预览 ── */}
          <section className="mb-16" id="界面预览">
            <h2 className="text-2xl font-bold mb-1 font-display">界面预览</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">Rest Reminder 核心界面一览</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="docs-card overflow-hidden">
                <div className="bg-[var(--bg)] p-8 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-12 h-12 rounded-full bg-[var(--accent-soft)] flex items-center justify-center text-2xl mx-auto mb-2">⚡</div>
                    <p className="text-xs text-[var(--fg-dim)]">浮球挂件</p>
                  </div>
                </div>
                <div className="p-3 border-t border-[var(--border)]">
                  <p className="text-xs text-[var(--fg-dim)]">60×60 桌面浮球，短点击弹出信息面板，长按拖动 reposition。休息时显示环形进度条。</p>
                </div>
              </div>
              <div className="docs-card overflow-hidden">
                <div className="bg-[var(--bg)] p-8 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-2xl font-bold font-display text-[var(--accent)] mb-2">⏱ 58:32</div>
                    <p className="text-[10px] text-[var(--fg-dim)]">学习倒计时</p>
                  </div>
                </div>
                <div className="p-3 border-t border-[var(--border)]">
                  <p className="text-xs text-[var(--fg-dim)]">主面板实时显示倒计时、学习时长、轮次、状态标签。每秒刷新，22:00 自动弹出每日汇报。</p>
                </div>
              </div>
              <div className="docs-card overflow-hidden">
                <div className="bg-[var(--bg)] p-8 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-8 rounded bg-[var(--accent-soft)] mb-2"></div>
                    <p className="text-[10px] text-[var(--fg-dim)]">趋势图表</p>
                  </div>
                </div>
                <div className="p-3 border-t border-[var(--border)]">
                  <p className="text-xs text-[var(--fg-dim)]">今日复盘时间线、周/月/季/年柱状图、7×24 学习热力图。鼠标悬浮查看具体数值。</p>
                </div>
              </div>
            </div>
          </section>

          {/* ── 功能说明 ── */}
          <section className="mb-16" id="功能说明">
            <h2 className="text-2xl font-bold mb-1 font-display">功能说明</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-8">深入了解每个功能的设计细节</p>

            <div className="space-y-5">
              <div className="docs-card" id="专注循环">
                <h3 className="text-sm font-semibold mb-2">⏱ 60 分钟专注循环</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  采用固定 60 分钟学习周期。60 分钟结束后进入 <strong>5 分钟请辨倒计时</strong>，浮层展示一条随机请辨金句，帮助你在休息前回顾学习内容。请辨结束后进入 <strong>5 分钟休息</strong>，休息结束后自动打开 B 站收藏夹视频。
                </p>
                <div className="mt-3 bg-[var(--surface)] rounded-lg p-4">
                  <p className="text-xs font-mono text-[var(--fg-dim)]">
                    计时规则：60min 学习 → 5min 请辨（金句） → 5min 休息 → B站视频 → 循环
                  </p>
                </div>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                  每 3 轮休息后自动打开护眼视频（BV14Y4y1N7PW），缓解长时间用眼疲劳。
                </p>
              </div>

              <div className="docs-card" id="护眼提醒">
                <h3 className="text-sm font-semibold mb-2">👁 20-20-20 护眼提醒</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  遵循眼科推荐的 <strong>20-20-20 法则</strong>：每学习 20 分钟，弹出轻量浮窗提醒看 6 米外 20 秒。浮窗 15 秒后自动消失，不打断学习流。可拖动到任意位置，下次启动记住位置。
                </p>
              </div>

              <div className="docs-card" id="学习追踪">
                <h3 className="text-sm font-semibold mb-2">📊 学习时长追踪与打卡</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  每次 60 分钟倒计时完成自动累计 1 小时学习时长。每日学习满 <strong>4 小时</strong> 完成打卡。
                </p>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3 space-y-1 list-disc list-inside">
                  <li><strong>连续打卡</strong>：每日达标自动累计，中断后从零开始</li>
                  <li><strong>里程碑金句</strong>：连续 1/3/7/14/30/60/90/365 天触发专属激励文案</li>
                  <li><strong>数据持久化</strong>：学习时长、休息时长、打卡记录全部存储在本地 JSON 文件</li>
                  <li><strong>请辨金句</strong>：休息前展示思辨金句，每日不重复循环</li>
                </ul>
              </div>

              <div className="docs-card" id="趋势分析">
                <h3 className="text-sm font-semibold mb-2">📈 趋势分析</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  5 个标签页提供多维度学习数据分析：
                </p>
                <div className="mt-3 space-y-2">
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">今日</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">复盘时间线 — 今天每次复盘的时间、评分、学科一览</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">周趋势</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">近 7 天学习时长柱状图，鼠标悬浮查看具体数值</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">月趋势</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">近 5 周学习时长趋势（周聚合）</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">季/年</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">近 6 个月月度趋势 + 总览统计</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">时段</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">各时段专注度对比 + 一周学习热力图（7天×24小时）</p>
                  </div>
                </div>
              </div>

              <div className="docs-card" id="ai分析">
                <h3 className="text-sm font-semibold mb-2">🤖 AI 学习分析</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  基于任意 OpenAI 兼容 API，根据你的学习数据自动生成深度分析报告。支持 <strong>日报/周报/月报/季报/年报</strong> 五级报告。
                </p>
                <div className="mt-3 bg-[var(--surface)] rounded-xl p-4">
                  <p className="text-sm font-semibold mb-2">每份报告包含</p>
                  <ul className="text-xs text-[var(--fg-dim)] leading-relaxed space-y-1 list-disc list-inside">
                    <li><strong>概览</strong> — 学习时长、完成轮次、复盘质量数据总结</li>
                    <li><strong>趋势分析</strong> — 学习节奏变化，结合复盘评分解释原因</li>
                    <li><strong>学科分布</strong> — 各学科投入情况分析</li>
                    <li><strong>改进建议</strong> — 5-7 条可落地的具体行动</li>
                    <li><strong>亮点总结</strong> — 肯定成就，指出可保持的优点</li>
                  </ul>
                </div>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                  未配置 API Key 时自动降级为本地数据摘要报告，确保功能可用。
                </p>
              </div>

              <div className="docs-card" id="使用技巧">
                <h3 className="text-sm font-semibold mb-2">💡 使用技巧</h3>
                <div className="space-y-3 mt-2">
                  <div>
                    <p className="text-sm font-medium text-[var(--fg)]">快捷键</p>
                    <p className="text-xs text-[var(--fg-dim)] mt-1">
                      Ctrl+Alt+P 暂停/继续学习计时，无需切换窗口。
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--fg)]">浮球交互</p>
                    <p className="text-xs text-[var(--fg-dim)] mt-1">
                      短点击浮球弹出信息面板（含开始/暂停按钮），长按拖动 reposition。休息时浮球显示琥珀色环形进度条。
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--fg)]">托盘控制</p>
                    <p className="text-xs text-[var(--fg-dim)] mt-1">
                      系统托盘右键菜单可补录复盘、打开信息面板、隐藏/退出程序。托盘图标 tooltip 实时显示倒计时和状态。
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--fg)]">电池监控</p>
                    <p className="text-xs text-[var(--fg-dim)] mt-1">
                      充电时弹窗提醒拔掉电源，保护电池健康。
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--fg)]">开机自启</p>
                    <p className="text-xs text-[var(--fg-dim)] mt-1">
                      设置中开启「开机自启」，程序随系统启动并在后台运行。
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* ── 设置详解 ── */}
          <section className="mb-16" id="设置详解">
            <h2 className="text-2xl font-bold mb-1 font-display">设置详解</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">每个选项的作用说明</p>

            <div className="space-y-3">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">🎯 学习计时</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  固定 60 分钟学习周期。包含 5 分钟请辨倒计时和 5 分钟休息，循环自动进行。
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">💬 请辨模式</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  休息前展示思辨金句，帮助你在休息前回顾学习内容。金句库每日不重复循环。
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">👁 20-20-20 护眼</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  每 20 分钟弹出护眼提醒浮窗，看 6 米外 20 秒，15 秒自动消失。可关闭。
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">📊 学习统计</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  开启后记录学习时长和休息时长，用于趋势分析和连续打卡。
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">📝 复盘提醒</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  每小时学习结束后弹出复盘评分弹窗，记录学科和标签。
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">🔊 声音提醒</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  休息提醒时播放提示音。休息音为轻柔两音符，倒计时结束为三音符上行琶音。
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">⚡ 开机自启</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  通过注册表实现开机自动启动。开启后程序随系统启动并在后台运行。
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">🤫 静默启动</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  启动后只显示浮球，不弹出主窗口。点击浮球弹出信息面板，显示倒计时与学习状态。
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">🗂 关闭最小化</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  关闭主窗口时最小化到系统托盘，而非退出程序。
                </p>
              </div>
            </div>
          </section>

          {/* ── 开发指南 ── */}
          <section className="mb-16" id="开发指南">
            <h2 className="text-2xl font-bold mb-1 font-display">开发指南</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">从源码构建和二次开发 Rest Reminder</p>

            <div className="space-y-5">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">环境要求</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li><strong>Python 3.14+</strong> — 核心依赖，必须使用 3.14 或更高版本</li>
                  <li><strong>PyQt5</strong> — GUI 框架（项目 vendor/ 目录已内嵌兼容版本）</li>
                  <li><strong>Windows 10/11</strong> — 使用 Win32 API（ctypes），仅支持 Windows</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">快速启动</h3>
                <pre className="bg-[var(--surface)] rounded-lg p-4 text-xs font-mono text-[#b5651d] overflow-x-auto">
{`git clone https://github.com/kuangketongxue/library-remind.git
cd library-remind
C:\\Python314\\python.exe rest_reminder.py --silent`}
                </pre>
                <p className="text-[var(--fg-dim)] text-xs mt-3 leading-relaxed">
                  注意：必须使用完整路径 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">C:\Python314\python.exe</code>，PATH 中的 python 可能指向其他版本，导致 ImportError。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">项目结构</h3>
                <div className="space-y-2">
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0 w-44">rest_reminder.py</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">主程序，约 8200 行，包含所有 UI 和业务逻辑</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0 w-44">storage.py</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">统一 JSON 存储层（JSONStore 类）</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0 w-44">tray_card.py</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">系统托盘卡片组件</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0 w-44">feishu_calendar.py</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">飞书日程集成模块</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0 w-44">vendor/</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">内嵌 PyQt5 等依赖（按 Python 3.14 ABI 编译）</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0 w-44">CLAUDE.md / AGENTS.md</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">AI 开发规则和踩坑记录</p>
                  </div>
                </div>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">状态机</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  程序基于四态循环状态机：<code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">idle → running → paused → resting → idle</code>。所有状态转换逻辑集中在主循环的 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">_tick()</code> 方法中。新增状态时需同步更新 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">_BTN_CONFIG</code>、对应的 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">_handle_*</code> 方法、以及主循环路由分支。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">构建 EXE</h3>
                <pre className="bg-[var(--surface)] rounded-lg p-4 text-xs font-mono text-[#b5651d] overflow-x-auto">
{`pyinstaller RestReminder.spec`}
                </pre>
                <p className="text-[var(--fg-dim)] text-xs mt-3 leading-relaxed">
                  spec 文件已配置好 hiddenimports 和 icon。构建产物在 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">dist/</code> 目录，约 48MB。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">代码规范</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li>改完代码后先 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">py_compile</code> 检查语法，再启动验证</li>
                  <li>所有数据文件使用 JSONStore 统一读写，不直接 open/write</li>
                  <li>PyQt 数值 API 只接受 int，float 必须显式 int() 转换</li>
                  <li><code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">from PyQt5 import sip</code>（不能用 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">import sip</code>，3.14 不兼容）</li>
                  <li>except 块必须有 log，不允许 bare <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">pass</code></li>
                </ul>
              </div>
            </div>
          </section>

          {/* ── Claude Code 接入指南 ── */}
          <section className="mb-16" id="claude-code">
            <h2 className="text-2xl font-bold mb-1 font-display">Claude Code 接入指南</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">使用 Claude Code 高效开发 Rest Reminder</p>

            <div className="space-y-5">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">项目配置</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  项目已配置 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">CLAUDE.md</code> 和 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">AGENTS.md</code>，Claude Code 打开项目目录后会自动加载开发规则、踩坑记录和关键配置位置。无需额外配置。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">开发工作流</h3>
                <ol className="text-[var(--fg-dim)] text-sm leading-relaxed list-decimal list-inside space-y-2">
                  <li>杀掉旧进程：<code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">taskkill /F /IM python.exe</code></li>
                  <li>语法检查：<code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">C:\Python314\python.exe -c "import py_compile; py_compile.compile('rest_reminder.py')"</code></li>
                  <li>启动程序：<code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">C:\Python314\python.exe rest_reminder.py --silent</code></li>
                  <li>验证进程：<code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">tasklist | findstr python.exe</code></li>
                  <li>检查崩溃日志：<code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">type crash.log</code></li>
                </ol>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">注意事项</h3>
                <div className="space-y-2">
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">Python 版本</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">必须用 3.14，PATH 中的 python 可能是其他版本</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">crash.log</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">第一调试入口，改完代码先看这里</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">多实例</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">Win32 Named Mutex 防护，崩溃自动释放</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">UI 修改</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">状态机改动需同步 _BTN_CONFIG + _handle_* + 路由分支</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* ── 更新日志 ── */}
          <section className="mb-16" id="更新日志">
            <h2 className="text-2xl font-bold mb-1 font-display">更新日志</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">最近几个重要版本</p>

            <div className="space-y-6">
              <div className="changelog-entry latest pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.6</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                  <span className="text-xs bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-0.5 rounded-full">最新</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>浏览器图标修复：favicon 换为 256x256 cute_icon.png</li>
                  <li>Contact 页面 framer-motion SSR 修复：内容不再透明不可见</li>
                  <li>Contact 页面使用 Gmail/WeChat 官方品牌图标</li>
                  <li>Hero 背景视频修复：静态图兜底 + 视频立即 autoPlay</li>
                  <li>公告弹窗每次访问弹出，文字颜色修复</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.5</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>AI 报告降级修复：服务不可用时显示本地数据摘要（学习时长/轮次/复盘）而非随机金句</li>
                  <li>Cloudflare Worker 重部署：AI 代理恢复正常</li>
                  <li>关终端不再退出应用：改用 pythonw.exe 后台启动</li>
                  <li>官网 Contact 等页面 404 修复：添加 fix-routes.js 构建后脚本</li>
                  <li>CI/CD 部署验证：自动测试所有页面和 AI 代理</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.4</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>AI 报告反幻觉修复：禁止编造老师姓名、学校、科目细节等虚构内容</li>
                  <li>所有结论必须引用具体数字</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.3</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>新增 /contact 联系页面：邮箱 + 微信二维码 + GitHub Issue 模板</li>
                  <li>新增 bug_report / feature_request / partnership 3 个 Issue 模板</li>
                  <li>文档页新增产品简介段 + 4 个数据卡片</li>
                  <li>导航栏新增「联系我们」链接</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.2</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>官网全面改版：暖奶油色背景 + WorkBuddy 风格 Footer + 三栏文档布局</li>
                  <li>导航栏新增「定价」链接 + 搜索按钮</li>
                  <li>Footer 重设计：Hero CTA + 4 栏导航（服务条款/文档指引/产品下载/联系我们）</li>
                  <li>文档页三栏布局：左侧导航 + 中间内容 + 右侧快速导航（滚动高亮）</li>
                  <li>文档页顶部搜索框（Enter 跳转匹配章节）</li>
                  <li>Navbar 文字适配深色背景（白色）</li>
                  <li>知识库清理：删除 7 个过期文件 + 新增 7 条经验记录</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.1</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>页面背景从纯白改为暖奶油色（#fdf6f0），长时间浏览不伤眼</li>
                  <li>CTA 横幅深棕渐变，白字清晰可见</li>
                  <li>底部粘性 CTA 栏适配暖色背景</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>修复 9 处 QFont CSS 字符串导致的主界面文字乱码（Georgia/Consolas 等字体失效回退）</li>
                  <li>修复飞书日历 lark-cli 路径亡址（指向已删 .workbuddy/ 目录）</li>
                  <li>AI 服务超时时自动 fallback 本地智慧语录（不再显示错误 toast，review 报告始终可用）</li>
                  <li>官网新增 pricing / privacy / rules / terms 法律合规 4 个独立页面</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.9</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-04</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>浮球 popup 飞书日程显示修复：root 重建 bug + 高度增大到 240</li>
                  <li>新增版本更新检查：启动后自动检测 GitHub 最新 release，有新版弹窗提示</li>
                  <li>修复 threading 模块未导入导致后台任务崩溃（影响 AI 报告 + 版本检查）</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.8</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-04</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>修复浮球 popup 关闭后再打开卡片空白</li>
                  <li>文档站 /docs 全面改版：Claude.ai 风格三栏布局</li>
                  <li>导航链接修复 + 硬编码颜色统一 + 死代码清理</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.7</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-04</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>修复 import copy 缺失导致设置保存崩溃</li>
                  <li>修复复盘弹窗 QSlider GC 崩溃（自动提交后评分丢失）</li>
                  <li>清理 _enter_rest() 重复通知</li>
                  <li>关于页 AI 服务动态展示真实 providers 列表</li>
                  <li>CLAUDE.md 与规格文档同步到 v6.x</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.6</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-03</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>设置保存防抖：300ms 内多次调用合并为一次磁盘写入</li>
                  <li>单实例锁删除 msvcrt 文件锁残留，仅用 Named Mutex</li>
                  <li>飞书日程 subprocess 改 Popen，stop() 可立即终止子进程</li>
                  <li>飞书日程缓存 24h→1h，避免跨天日程不刷新</li>
                  <li>修复邮件测试连点堆叠 QThread 崩溃、JSONStore 并发写丢 key</li>
                  <li>md_to_html 接受 theme 参数，light 主题报告不再显示 dark 底色</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.4</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-02</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>修复 AI 服务不可用：default_proxy 被禁用后重启仍不可用</li>
                  <li>修复设置页测试连接卡顿：HTTP 请求改后台线程，UI 不再冻结</li>
                  <li>浮球短点击切换显示/隐藏，右键菜单动态文案</li>
                  <li>托盘菜单新增浮球显示切换</li>
                  <li>浮球 popup 扩容到 260×200，22:00 进度条改为倒计时模式</li>
                  <li>飞书刷新按钮对比度修复，侧边栏矢量图标，GitHub 真实图标</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.3</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-02</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>修复计时漂移：引入 time.perf_counter() 统一计时源</li>
                  <li>修复临时文件泄漏：_TempFileManager 集中注册 + atexit 清理</li>
                  <li>增强日志归档：按日期自动归档旧日志</li>
                  <li>Sponsor 区重构：真实技术生态 + 文档 FAQ 赞助合作</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.2</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-01</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>修复趋势图完全空白（延迟加载后初始数据未加载）</li>
                  <li>修复设置 Tab 错误显示趋势内容（索引错位）</li>
                  <li>官网下载截图替换为 GitHub Releases 页面</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.0.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-30</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>主界面去置顶 + AI 服务自定义提供商</li>
                  <li>内置免费 AI（Cloudflare 代理，key 隐藏）</li>
                  <li>成就扩充 16→19 个，进度条优化</li>
                  <li>GitHub 自动备份 + 官网优化</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v5.6.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-30</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>成就显示优化：卡片式展示 + 进度条 + 当前进度文本</li>
                  <li>环境白噪音：30 秒循环、首尾 crossfade 消除循环断裂</li>
                  <li>邮件周报改用 Agent QQ 邮箱（agently-cli），移除 SMTP</li>
                  <li>关于界面字体放大，环境/数据/AI 服务信息清晰可见</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v5.5.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-29</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>成就/徽章系统：16 个成就，解锁 Toast 通知</li>
                  <li>GitHub 风格学习热力图：52 周 × 7 天，5 级颜色</li>
                  <li>环境白噪音：雨声/森林/咖啡厅/白噪音/棕噪音</li>
                  <li>每周邮件周报：SMTP 配置，HTML 格式 AI 学习报告</li>
                  <li>主题切换：深色/浅色/跟随系统</li>
                  <li>全局快捷键：Ctrl+Alt+P/S/B，Ctrl+1~5 切换 Tab</li>
                  <li>API Key 加密存储（XOR + 机器盐值）</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v5.4.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-29</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>飞书日程集成：实时显示当前/下一个日程</li>
                  <li>趋势时间选择器：近7/14/30天 + 自定义日期范围</li>
                  <li>AI API Key 配置界面、SenseNova 推理模型兼容</li>
                  <li>修复任务栏图标丢失、多实例启动竞态</li>
                  <li>「关于」「趋势」页面重新设计</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v5.1.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-26</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>主界面全面实时刷新：学习时长/轮次/休息时长/状态/倒计时每秒更新</li>
                  <li>修复复盘摘要空列表崩溃、连续打卡恢复逻辑错误</li>
                  <li>修复月趋势/季年趋势统计错误</li>
                  <li>删除死代码，移除失效窗口按钮</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v5.0.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-25</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>柱状图悬浮提示、复盘学科新增「其他」</li>
                  <li>AI 报告后台线程（QThread 异步），趋势分析全面重构</li>
                  <li>AI 报告字数提升至 400+ 字，增加 5 个分析章节</li>
                  <li>修复 AI 报告卡死、tooltip 不显示等 P0 bug</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v4.4.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-23</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>5 标签页主界面（今日/AI报告/趋势/设置/关于）</li>
                  <li>⚡ 浮球独立（60×60）、点击弹出信息面板</li>
                  <li>20-20-20 护眼浮窗、热力图、B站收藏夹</li>
                  <li>开源发布：移除 Pro 订阅系统，MIT 协议全部免费</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v4.3.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-21</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>固定 60 分钟学习 → 5 分钟请辨 → 5 分钟休息循环</li>
                  <li>每 3 轮自动播放护眼视频</li>
                  <li>休息期间弹出复盘评分（学科 + 标签 + 1-100 评分）</li>
                </ul>
              </div>
            </div>

            <p className="text-[var(--fg-dim)] text-sm mt-6">
              完整更新日志（含 v3.0-v5.1 全部版本）见{" "}
              <a
                href="https://github.com/kuangketongxue/library-remind/blob/main/CHANGELOG.md"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[var(--accent)] hover:underline"
              >
                GitHub CHANGELOG.md
              </a>
            </p>
          </section>

          {/* ── 常见问题 ── */}
          <section className="mb-16" id="常见问题">
            <h2 className="text-2xl font-bold mb-1 font-display">常见问题</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">遇到问题？看看这里有没有答案</p>

            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">程序启动后只看到浮球，主界面不显示？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">正常行为。默认静默启动只显示右下角浮球，点击浮球弹出信息面板。如需启动即显示主窗口，在设置中关闭「静默启动」。</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">B 站收藏夹没打开？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">检查设置中的 B 站收藏夹 ID（fid）和用户 ID（mid）是否正确。默认使用项目内置的收藏夹，如需更换请在设置中修改。</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">AI 报告生成失败？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">检查设置中是否配置了 SenseNova API Key。未配置时自动使用本地数据摘要报告，不会报错。可在「关于」页面的环境诊断中检查依赖状态。</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">复盘评分的数据存在哪里？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">所有复盘数据存储在程序同目录的 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">.review_log.json</code> 中。每轮学习结束后自动追加记录，包含时间、学科、标签和评分。</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">如何卸载？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  直接删除程序文件夹即可。如开启了开机自启，请先运行 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">uninstall.bat</code> 清除注册表项，再删除文件夹。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">数据会丢失吗？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">所有数据存储在本地 JSON 文件，重启电脑不丢失。重装系统前建议备份程序目录下的 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">.daily_log.json</code>、<code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">.review_log.json</code>、<code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">.streak.json</code> 等文件。</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">支持 macOS / Linux 吗？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">目前仅支持 Windows 10/11（基于 PyQt5 和 Windows API）。macOS 和 Linux 版本正在规划中。</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">需要联网才能用吗？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">核心功能（休息提醒、护眼、学习追踪、趋势分析）完全离线运行。只有 AI 学习分析需要联网调用 SenseNova API，其余功能全部本地可用。</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">连续打卡中断了怎么办？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">连续打卡基于每日学习时长判断（满 4 小时算一天）。如果某天未达标，连续天数归零，最佳记录保留。第二天达标后重新开始累计。</p>
              </div>

              {/* ── 赞助合作 ── */}
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">如何成为赞助商？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  我们欢迎 API 服务、工具产品或其他形式的合作。请发送邮件至 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">kuangketongxue@gmail.com</code>，注明合作意向和联系方式，我们会在 3 个工作日内回复。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">有哪些合作方案？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  支持多种合作形式：GitHub README 广告位、应用内预置接入、官网赞助商展示、优先技术支持等。具体方案可根据赞助商的资源和需求定制。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">完成洽谈后多久可以上线？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  根据合作内容不同，通常 1-2 周内完成接入和上线。简单的 API 接入可更快完成，复杂的定制化合作可能需要更长时间。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">赞助商可以获得什么？</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  赞助商可获得 GitHub README 广告位、应用内预置接入、官网赞助商展示、优先技术支持等权益。具体权益根据赞助等级和合作形式确定。
                </p>
              </div>
            </div>
          </section>

          {/* ── 故障排除 ── */}
          <section className="mb-16" id="故障排除">
            <h2 className="text-2xl font-bold mb-1 font-display">故障排除</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">常见问题排查步骤</p>

            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">浮球不显示 / 点击无反应</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">按以下步骤排查：</p>
                <ol className="text-xs text-[var(--fg-dim)] leading-relaxed list-decimal list-inside space-y-1">
                  <li>检查程序是否在运行：查看系统托盘是否有图标。</li>
                  <li>右键点击托盘图标 → 选择「⚡ 显示浮球」。</li>
                  <li>若托盘图标也不存在，检查是否被安全软件拦截。</li>
                  <li>重启程序，确保无 crash.log 生成。</li>
                </ol>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">AI 报告生成失败 / 卡死</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">按以下步骤排查：</p>
                <ol className="text-xs text-[var(--fg-dim)] leading-relaxed list-decimal list-inside space-y-1">
                  <li>进入「设置 → AI 服务」检查 API Key 是否配置正确。</li>
                  <li>检查网络连接，确保能访问 API 端点。</li>
                  <li>未配置 Key 时自动降级为本地数据摘要，不会报错。若仍异常，查看 crash.log。</li>
                  <li>在「关于」页面的环境诊断中检查依赖状态。</li>
                </ol>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">倒计时不准 / 计时漂移</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  程序使用 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">time.perf_counter()</code> 作为计时源，长时间运行误差极小。若发现明显不准，请确认没有通过任务管理器强制暂停 python.exe 进程。
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">B 站收藏夹没打开</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">按以下步骤排查：</p>
                <ol className="text-xs text-[var(--fg-dim)] leading-relaxed list-decimal list-inside space-y-1">
                  <li>检查设置中的 B 站收藏夹 ID（fid）和用户 ID（mid）是否正确。</li>
                  <li>确认默认浏览器可正常启动。</li>
                  <li>尝试手动打开收藏夹链接：<code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">https://space.bilibili.com/529362421/favlist?fid=3648313921</code></li>
                  <li>如收藏夹为私有，请确保账号已登录。</li>
                </ol>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">数据丢失 / 重装后恢复</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  所有数据存储在程序同目录的 <code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">.daily_log.json</code>、<code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">.review_log.json</code>、<code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">.streak.json</code>。重装前请备份这些文件。
                </p>
              </div>
            </div>
          </section>

          {/* ── 底部导航 ── */}
          <nav className="border-t border-[var(--border)] pt-8 mt-16 flex flex-col sm:flex-row justify-between gap-4">
            <a href="#更新日志" className="group flex items-center gap-3 text-sm">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <div>
                <p className="text-[var(--fg-muted)] text-xs">上一页</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">更新日志</p>
              </div>
            </a>
            <a href="#" className="group flex items-center gap-3 text-sm sm:flex-row-reverse">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <div className="sm:text-right">
                <p className="text-[var(--fg-muted)] text-xs">回到顶部</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">回到顶部</p>
              </div>
            </a>
          </nav>
        </div>

        {/* 右侧快速导航 */}
        <DocsTOC />

      </div>
    </main>
  );
}