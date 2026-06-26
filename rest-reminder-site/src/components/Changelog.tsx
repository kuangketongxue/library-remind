"use client";

const releases = [
  {
    version: "v5.1",
    date: "2026.06.26",
    tag: "最新",
    changes: [
      "主界面全面实时刷新：学习时长/轮次/休息时长/状态/倒计时每秒更新",
      "修复复盘摘要空列表崩溃（无数据时 TypeError）",
      "修复连续打卡恢复逻辑：历史恢复后 +1 重复导致数字跳变",
      "修复月趋势周聚合越界 + 季/年统计天数不匹配",
      "删除死代码 _show_ai_report（~90行），移除失效最大化按钮",
    ],
  },
  {
    version: "v5.0",
    date: "2026.06.25",
    tag: "最新",
    changes: [
      "修复 AI 报告卡死：_md_to_html 方法位置错误导致报告界面永远显示「正在生成」",
      "趋势分析全面重构：彻底移除电脑使用时长统计，改为纯学习时长单柱图",
      "新增柱状图悬浮提示：鼠标移到任意柱子即可看到具体学习时长数值",
      "浮球图标改为 ⚡ 闪电符号",
      "复盘学科新增「其他」选项，支持复盘/健身/阅读等非学科场景",
      "优化 AI 请求错误处理：区分网络错误、响应解析错误，更精准的报错信息",
      "修复 PyQt5 sip 导入兼容性问题（Python 3.14 适配）",
      "代码质量：移除冗余代码、修复重复方法定义、统一变量命名",
    ],
  },
  {
    version: "v4.4",
    date: "2026.06.23",
    tag: "",
    changes: [
      "修复启动崩溃（QTextBrowser 缺失 import），开机自启动恢复正常",
      "趋势窗口新增热力图（一周时段分布）",
      "复盘弹窗优化：更大按钮 + 金色选中态 + 15秒倒计时 + 信息栏",
      "轮次目标弹窗优化：15秒自动提交 + 实时倒计时显示",
      "AI 报告后台线程生成，不再卡顿 UI（QThread）",
      "文本缓存优化：浮球文字变化时才更新，消除 repaint storm",
      "移除趋势 tab 底部冗余按钮（查看详细趋势/复盘时间线）",
      "修复 excepthook 导致随机崩溃（移除 sys.exit(1)）",
      "emoji 字体修复：全局添加 Segoe UI Emoji",
      "窗口标题动态显示当前 tab",
      "更新官网域名至 crazy-rest-reminder.pages.dev",
      "开源发布：移除 Pro 订阅系统，全部功能免费",
    ],
  },
  {
    version: "v4.3",
    date: "2026.06.21",
    tag: "",
    changes: [
      "UI 重构：5 标签页（今日概览/AI报告/趋势/设置/关于）",
      "今日标签：直接展示学习时长、轮次、休息状态、复盘、连续天数",
      "AI 报告：直接展示日报/周报/月报/季报/年报，无需额外点击",
      "完全免费：移除 Pro 订阅系统，所有功能直接可用",
      "修复：趋势图表空白、设置不持久化、托盘按钮不可点击等 8 个 bug",
    ],
  },
  {
    version: "v4.0",
    date: "2026.06",
    tag: "",
    changes: [
      "全新 2x2 卡片化主界面",
      "20-20-20 护眼提醒：每 20 分钟轻量浮窗看远处",
      "趋势分析：5 标签页（今日/周/月/季年/时段）",
      "趋势分析：5 标签页（今日/周/月/季年/时段）",
      "请辨金句模式 + 每小时复盘",
      "AI 学习分析：自动生成日报/周报/月报/季报/年报",
    ],
  },
  {
    version: "v3.3",
    date: "2026.06",
    tag: "",
    changes: [
      "移除看门狗，注册表直启更稳定",
      "功能模块化重构",
    ],
  },
  {
    version: "v3.2",
    date: "2026.06",
    tag: "",
    changes: [
      "用户可配置 B站收藏夹和提醒视频",
      "设置页面：右键菜单可视化配置",
    ],
  },
  {
    version: "v3.1",
    date: "2026.05",
    tag: "",
    changes: [
      "学习数据追踪：每日学习时长",
      "连续打卡天数统计",
      "跨重启状态续接",
      "开机自启",
    ],
  },
  {
    version: "v3.0",
    date: "2026.04",
    tag: "",
    changes: [
      "全新暗色调主题",
      "B站护眼视频自动播放",
      "自定义收藏夹支持",
      "性能优化：内存占用降低 40%",
    ],
  },
  {
    version: "v2.0",
    date: "2026.03",
    tag: "",
    changes: [
      "首次发布",
      "60 分钟自动循环计时",
      "休息提醒弹窗",
      "基础设置面板",
    ],
  },
];

export default function Changelog() {
  return (
    <section className="py-20 px-6 border-t border-[var(--border)]" id="changelog">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-center mb-12 font-display">更新日志</h2>

        <div className="relative">
          <div className="absolute left-[7px] top-0 bottom-0 w-px bg-[var(--border)]" />

          <div className="space-y-8">
            {releases.map((r) => (
              <div key={r.version} className="relative pl-10">
                <div className="absolute left-0 top-1 w-[15px] h-[15px] rounded-sm bg-[var(--accent)]" />

                <div className="flex items-center gap-3 mb-2">
                  <span className="text-base font-bold font-display tracking-tight">{r.version}</span>
                  <span className="text-[12px] text-[var(--fg-dim)] font-mono">{r.date}</span>
                  {r.tag && (
                    <span className="text-[10px] font-semibold text-[var(--accent)] bg-[var(--accent-soft)] px-1.5 py-0.5 rounded border border-[var(--border)]">
                      {r.tag}
                    </span>
                  )}
                </div>

                <ul className="space-y-1.5">
                  {r.changes.map((c, i) => (
                    <li key={i} className="flex items-start gap-2.5 text-[13px] text-[var(--fg-dim)]">
                      <span className="text-[var(--accent)] mt-0.5 text-[10px]">+</span>
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
