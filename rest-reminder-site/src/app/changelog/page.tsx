import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "更新日志 — 精力管理 Chrome 扩展",
  description: "「精力管理」Chrome 扩展的所有版本更新记录，包含新功能、修复、合规等",
};

const RELEASES = [
  {
    version: "v1.3.0",
    date: "2026-07-13",
    tag: "功能补齐 + 体验升级",
    sections: [
      {
        title: "🆕 新功能",
        items: [
          "休息倒计时弹窗：rest.html 5 分钟弹窗，圆环进度条 + 横条进度 + 大字倒计时 + 智能提示语",
          "声音提醒：休息和复盘开始时播放和弦铃音，设置页可关",
          "暂停超时提醒：暂停超过 2 分钟弹桌面通知",
          "自动开始下一轮：复盘提交后 3 秒自动续接（可关，默认关）",
          "灰阶滤镜：专注期间所有标签页变灰（grayscale 100%），popup 一键开关",
          "动态工具栏图标：OffscreenCanvas 生成圆环进度 + 剩余分钟数",
          "深度专注评分：深度分 = 自评分 × 完成度 × 专注度 × 连续性，三因子实时展示",
        ],
      },
      {
        title: "🔧 设置页修复",
        items: [
          "设置真正生效：学习/休息/护眼间隔从写死改为读取 storage",
          "新增设置项：休息提示音开关、自动开始下一轮开关",
        ],
      },
      {
        title: "🔒 合规",
        items: [
          "隐私政策上线：crazy-rest-reminder.pages.dev/privacy-chrome",
          "CWS 上架指南：权限说明、商品详情文案、打包清单模板",
          "manifest 清理：删除 web_accessible_resources: <all_urls>、加 minimum_chrome_version: 88",
        ],
      },
    ],
  },
  {
    version: "v1.2.0",
    date: "2026-07-10",
    tag: "完整功能版",
    sections: [
      {
        title: "🚀 核心功能",
        items: [
          "60+5 分钟学习循环",
          "复盘评分 1-100 + 学科/标签",
          "B 站联动 + 护眼视频",
          "20-20-20 护眼提醒",
          "Badge 倒计时 + 22:00 硬限制",
        ],
      },
      {
        title: "🎯 数据与统计",
        items: [
          "连续打卡 + 轮次目标提示",
          "趋势分析（近 7 天柱状图）",
          "成就系统（16 个徽章）",
          "AI 学习报告（日报/周报/月报/季报）",
        ],
      },
      {
        title: "💾 集成",
        items: [
          "GitHub 备份/恢复",
          "飞书日历",
          "邮件周报",
          "B 站链接可配置",
        ],
      },
    ],
  },
];

export default function ChangelogPage() {
  return (
    <main className="flex-1">
      <div className="max-w-3xl mx-auto px-6 py-20 animate-[fadeInUp_0.5s_ease-out]">
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-2 font-display">
          更新日志
        </h1>
        <p className="text-[var(--fg-dim)] mb-12">所有版本更新记录。</p>

        <div className="space-y-12">
          {RELEASES.map((release) => (
            <article key={release.version} className="docs-card p-8">
              <div className="flex items-baseline gap-3 mb-4">
                <h2 className="text-2xl font-bold">{release.version}</h2>
                <span className="text-sm text-[var(--fg-dim)]">{release.date}</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-[var(--accent-soft)] text-[var(--accent)]">
                  {release.tag}
                </span>
              </div>
              <div className="space-y-5">
                {release.sections.map((section) => (
                  <section key={section.title}>
                    <h3 className="text-lg font-semibold mb-2">{section.title}</h3>
                    <ul className="space-y-1.5">
                      {section.items.map((item) => (
                        <li key={item} className="text-[var(--fg-dim)] text-sm flex gap-2">
                          <span className="text-[var(--accent)]">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </section>
                ))}
              </div>
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}
