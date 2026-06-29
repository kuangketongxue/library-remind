"use client";

import DocsNav from "@/components/DocsNav";
import DocsTOC, { type TocItem } from "@/components/DocsTOC";

const tocItems: TocItem[] = [
  { id: "快速开始", label: "快速开始", level: 2 },
  { id: "下载运行", label: "1. 下载运行", level: 3 },
  { id: "设定目标", label: "2. 设定目标", level: 3 },
  { id: "开始学习", label: "3. 开始学习", level: 3 },
  { id: "复盘追踪", label: "4. 复盘追踪", level: 3 },
  { id: "功能说明", label: "功能说明", level: 2 },
  { id: "专注循环", label: "60 分钟专注循环", level: 3 },
  { id: "护眼提醒", label: "20-20-20 护眼提醒", level: 3 },
  { id: "学习追踪", label: "学习时长追踪与打卡", level: 3 },
  { id: "趋势分析", label: "趋势分析", level: 3 },
  { id: "ai分析", label: "AI 学习分析", level: 3 },
  { id: "使用技巧", label: "使用技巧", level: 3 },
  { id: "设置详解", label: "设置详解", level: 2 },
  { id: "更新日志", label: "更新日志", level: 2 },
  { id: "常见问题", label: "常见问题", level: 2 },
];

export default function DocsPage() {
  return (
    <main className="flex-1">
      <div className="max-w-6xl mx-auto flex">
        {/* 左侧导航 */}
        <DocsNav />

        {/* 中间内容 */}
        <div className="flex-1 min-w-0 px-6 py-12">
          <div className="max-w-3xl">
            <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">
              文档
            </h1>
            <p className="text-[var(--fg-dim)] mb-10">
              Rest Reminder 完整使用指南，从快速上手到高级功能。
            </p>

            {/* ── 快速开始 ── */}
            <section className="mb-16" id="快速开始">
              <h2 className="text-2xl font-bold mb-1 font-display">快速开始</h2>
              <p className="text-[var(--fg-dim)] text-sm mb-6">5 分钟上手 Rest Reminder</p>

              <div className="space-y-8">
                <div id="下载运行">
                  <h3 className="text-base font-semibold mb-3 font-display">1. 下载运行</h3>
                  <div className="bg-[var(--surface-raised)] rounded-xl p-5 mb-3">
                    <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-3">
                      双击 <code className="bg-[var(--bg)] px-1.5 py-0.5 rounded text-xs font-mono">_launch.vbs</code> 启动程序。
                      无需安装 Python，无需额外依赖。
                    </p>
                    <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                      如果从源码运行，确保已安装依赖：
                    </p>
                    <pre className="bg-[var(--bg)] rounded-lg p-4 mt-3 text-xs font-mono text-[var(--accent)] overflow-x-auto">
{`pip install -r requirements.txt
python rest_reminder.py`}
                    </pre>
                  </div>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                    首次运行会在程序目录创建数据文件（<code className="bg-[var(--surface-raised)] px-1 py-0.5 rounded text-xs font-mono">.daily_log.json</code>、<code className="bg-[var(--surface-raised)] px-1 py-0.5 rounded text-xs font-mono">.review_log.json</code> 等），用于持久化学习数据。
                  </p>
                </div>

                <div id="设定目标">
                  <h3 className="text-base font-semibold mb-3 font-display">2. 设定今日目标</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                    启动后弹出目标设置对话框。输入今天主要学习内容（如"数学导数+英语阅读"），选择预计完成轮次。
                    目标会显示在浮球信息面板中，提醒你当前进度。
                  </p>
                  <div className="bg-[var(--surface-raised)] rounded-xl p-4 mt-3">
                    <p className="text-xs text-[var(--fg-dim)]">
                      <span className="text-[var(--accent)]">提示：</span>
                      目标是可选的。跳过不影响计时功能，随时可从主界面或浮球面板重新设定。
                    </p>
                  </div>
                </div>

                <div id="开始学习">
                  <h3 className="text-base font-semibold mb-3 font-display">3. 开始学习</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                    程序默认以浮球形式驻留桌面右侧。点击浮球弹出信息面板，按 <code className="bg-[var(--surface-raised)] px-1.5 py-0.5 rounded text-xs font-mono">▶ 开始学习</code> 启动 60 分钟倒计时。
                  </p>
                  <div className="bg-[var(--surface-raised)] rounded-xl p-5 mt-3">
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
                    <div className="border border-[var(--border)] rounded-xl p-4">
                      <p className="text-sm font-semibold mb-1">📝 复盘评分</p>
                      <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                        滑块选择 1-100 分评分，记录学科（语/数/英/物/化/政/其他）和标签（专注/疲劳/收获大/走神/其他）。
                        数据持久化到本地，供趋势分析和 AI 报告使用。
                      </p>
                    </div>
                    <div className="border border-[var(--border)] rounded-xl p-4">
                      <p className="text-sm font-semibold mb-1">🔥 连续打卡</p>
                      <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                        每日学习满 4 小时自动打卡。连续打卡到达里程碑（1/3/7/14/30/60/90/365 天）时展示特殊金句奖励。
                        中断后重新开始计数。
                      </p>
                    </div>
                    <div className="border border-[var(--border)] rounded-xl p-4">
                      <p className="text-sm font-semibold mb-1">📊 实时数据</p>
                      <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                        「今日」tab 每秒刷新学习时长、当前轮次、休息时长、状态标签。
                        22:00 自动弹出每日学习汇报。
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* ── 功能说明 ── */}
            <section className="mb-16" id="功能说明">
              <h2 className="text-2xl font-bold mb-1 font-display">功能说明</h2>
              <p className="text-[var(--fg-dim)] text-sm mb-8">深入了解每个功能的设计细节</p>

              <div className="space-y-5">
                <div className="border border-[var(--border)] rounded-xl p-6" id="专注循环">
                  <h3 className="text-sm font-semibold mb-2">⏱ 60 分钟专注循环</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                    采用固定 60 分钟学习周期。60 分钟结束后进入 <strong>5 分钟请辨倒计时</strong>，
                    浮层展示一条随机请辨金句，帮助你在休息前回顾学习内容。
                    请辨结束后进入 <strong>5 分钟休息</strong>，休息结束后自动打开 B 站收藏夹视频。
                  </p>
                  <div className="mt-3 bg-[var(--bg)] rounded-lg p-4">
                    <p className="text-xs font-mono text-[var(--fg-dim)]">
                      计时规则：60min 学习 → 5min 请辨（金句） → 5min 休息 → B站视频 → 循环
                    </p>
                  </div>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                    每 3 轮休息后自动打开护眼视频（<code className="bg-[var(--surface-raised)] px-1 py-0.5 rounded text-xs font-mono">BV14Y4y1N7PW</code>），
                    缓解长时间用眼疲劳。
                  </p>
                </div>

                <div className="border border-[var(--border)] rounded-xl p-6" id="护眼提醒">
                  <h3 className="text-sm font-semibold mb-2">👁 20-20-20 护眼提醒</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                    遵循眼科推荐的 <strong>20-20-20 法则</strong>：每学习 20 分钟，弹出轻量浮窗提醒看 6 米外 20 秒。
                    浮窗 15 秒后自动消失，不打断学习流。可拖动到任意位置，下次启动记住位置。
                  </p>
                </div>

                <div className="border border-[var(--border)] rounded-xl p-6" id="学习追踪">
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

                <div className="border border-[var(--border)] rounded-xl p-6" id="趋势分析">
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

                <div className="border border-[var(--border)] rounded-xl p-6" id="ai分析">
                  <h3 className="text-sm font-semibold mb-2">🤖 AI 学习分析</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                    基于 SenseNova API，根据你的学习数据自动生成深度分析报告。支持 <strong>日报/周报/月报/季报/年报</strong> 五级报告。
                  </p>
                  <div className="mt-3 bg-[var(--surface-raised)] rounded-xl p-4">
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

                <div className="border border-[var(--border)] rounded-xl p-6" id="使用技巧">
                  <h3 className="text-sm font-semibold mb-2">💡 使用技巧</h3>
                  <div className="space-y-3 mt-2">
                    <div>
                      <p className="text-sm font-medium text-[var(--fg)]">快捷键</p>
                      <p className="text-xs text-[var(--fg-dim)] mt-1">
                        <code className="bg-[var(--surface-raised)] px-1.5 py-0.5 rounded text-xs font-mono">Ctrl+Alt+P</code> 暂停/继续学习计时，无需切换窗口。
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-[var(--fg)]">浮球交互</p>
                      <p className="text-xs text-[var(--fg-dim)] mt-1">
                        短点击浮球弹出信息面板（含开始/暂停按钮），长按拖动 reposition。
                        休息时浮球显示琥珀色环形进度条。
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-[var(--fg)]">托盘控制</p>
                      <p className="text-xs text-[var(--fg-dim)] mt-1">
                        系统托盘右键菜单可补录复盘、打开主界面、隐藏/退出程序。
                        托盘图标 tooltip 实时显示倒计时和状态。
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
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">🎯 学习计时</h3>
                  <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                    固定 60 分钟学习周期。包含 5 分钟请辨倒计时和 5 分钟休息，循环自动进行。
                  </p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">💬 请辨模式</h3>
                  <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                    休息前展示思辨金句，帮助你在休息前回顾学习内容。金句库每日不重复循环。
                  </p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">👁 20-20-20 护眼</h3>
                  <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                    每 20 分钟弹出护眼提醒浮窗，看 6 米外 20 秒，15 秒自动消失。可关闭。
                  </p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">📊 学习统计</h3>
                  <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                    开启后记录学习时长和休息时长，用于趋势分析和连续打卡。
                  </p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">📝 复盘提醒</h3>
                  <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                    每小时学习结束后弹出复盘评分弹窗，记录学科和标签。
                  </p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">🔊 声音提醒</h3>
                  <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                    休息提醒时播放提示音。休息音为轻柔两音符，倒计时结束为三音符上行琶音。
                  </p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">⚡ 开机自启</h3>
                  <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                    通过注册表实现开机自动启动。开启后程序随系统启动并在后台运行。
                  </p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">🤫 静默启动</h3>
                  <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                    启动后只显示浮球，不弹出主窗口。点击浮球打开主界面。
                  </p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-1">🗂 关闭最小化</h3>
                  <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                    关闭主窗口时最小化到系统托盘，而非退出程序。
                  </p>
                </div>
              </div>
            </section>

            {/* ── 更新日志 ── */}
            <section className="mb-16" id="更新日志">
              <h2 className="text-2xl font-bold mb-1 font-display">更新日志</h2>
              <p className="text-[var(--fg-dim)] text-sm mb-6">最近几个重要版本</p>

              <div className="space-y-6">
                <div className="border-l-2 border-[var(--accent)] pl-4">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-bold">v5.6.0</span>
                    <span className="text-xs text-[var(--fg-dim)]">2026-06-30</span>
                    <span className="text-xs bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-0.5 rounded-full">最新</span>
                  </div>
                  <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                    <li>成就显示优化：卡片式展示 + 进度条 + 当前进度文本</li>
                    <li>环境白噪音：30 秒循环、首尾 crossfade 消除循环断裂</li>
                    <li>邮件周报改用 Agent QQ 邮箱（agently-cli），移除 SMTP</li>
                    <li>关于界面字体放大，环境/数据/AI 服务信息清晰可见</li>
                  </ul>
                </div>

                <div className="border-l-2 border-[var(--border)] pl-4">
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

                <div className="border-l-2 border-[var(--border)] pl-4">
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

                <div className="border-l-2 border-[var(--border)] pl-4">
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

                <div className="border-l-2 border-[var(--border)] pl-4">
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

                <div className="border-l-2 border-[var(--border)] pl-4">
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

                <div className="border-l-2 border-[var(--border)] pl-4">
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
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">检查设置中是否配置了 SenseNova API Key。未配置时自动使用本地数据摘要报告，不会报错。可在「关于」页面的环境诊断中检查依赖状态。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-2">复盘评分的数据存在哪里？</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">所有复盘数据存储在程序同目录的 <code className="bg-[var(--surface-raised)] px-1 py-0.5 rounded text-xs font-mono">.review_log.json</code> 中。每轮学习结束后自动追加记录，包含时间、学科、标签和评分。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-2">数据会丢失吗？</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">所有数据存储在本地 JSON 文件，重启电脑不丢失。重装系统前建议备份程序目录下的 <code className="bg-[var(--surface-raised)] px-1 py-0.5 rounded text-xs font-mono">.daily_log.json</code>、<code className="bg-[var(--surface-raised)] px-1 py-0.5 rounded text-xs font-mono">.review_log.json</code>、<code className="bg-[var(--surface-raised)] px-1 py-0.5 rounded text-xs font-mono">.streak.json</code> 等文件。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-2">支持 macOS / Linux 吗？</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">目前仅支持 Windows 10/11（基于 PyQt5 和 Windows API）。macOS 和 Linux 版本正在规划中。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-2">需要联网才能用吗？</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">核心功能（休息提醒、护眼、学习追踪、趋势分析）完全离线运行。只有 AI 学习分析需要联网调用 SenseNova API，其余功能全部本地可用。</p>
                </div>
                <div className="border border-[var(--border)] rounded-xl p-5">
                  <h3 className="text-sm font-semibold mb-2">连续打卡中断了怎么办？</h3>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">连续打卡基于每日学习时长判断（满 4 小时算一天）。如果某天未达标，连续天数归零，最佳记录保留。第二天达标后重新开始累计。</p>
                </div>
              </div>
            </section>
          </div>
        </div>

        {/* 右侧 TOC */}
        <div className="hidden xl:block w-48 shrink-0">
          <DocsTOC items={tocItems} />
        </div>
      </div>
    </main>
  );
}
