"use client";

const releases = [
  {
    version: "v4.4",
    date: "2026.06",
    tag: "最新",
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
      "活动密度感知：连续活跃自动缩至 45min，空闲 5min 自动暂停",
      "趋势分析：5 标签页（今日/周/月/季年/时段）",
      "请辨金句模式+每小时复盘",
      "AI 学习分析：自动生成日报/周报/月报/季报/年报",
    ],
  },
  {
    version: "v3.3",
    date: "2026.06",
    tag: "",
    changes: [
      "移除看门狗，注册表直启更稳定",
      "Pro 版功能重构",
    ],
  },
  {
    version: "v3.2",
    date: "2026.06",
    tag: "",
    changes: [
      "用户可配置B站收藏夹和提醒视频",
      "设置页面：右键菜单可视化配置",
    ],
  },
  {
    version: "v3.1",
    date: "2026.05",
    tag: "",
    changes: [
      "学习数据追踪：每日学习/电脑/休息时长",
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
      "性能优化：内存占用降低40%",
    ],
  },
  {
    version: "v2.0",
    date: "2026.03",
    tag: "",
    changes: [
      "首次发布",
      "60分钟自动循环计时",
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
