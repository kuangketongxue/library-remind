"use client";

const releases = [
  {
    version: "v6.1.2",
    date: "2026.07.01",
    tag: "最新",
    changes: [
      "修复趋势图完全空白（延迟加载后初始数据未加载）",
      "官网下载截图替换为 GitHub Releases 页面",
    ],
  },
  {
    version: "v6.1.1",
    date: "2026.07.01",
    tag: "",
    changes: [
      "修复设置 Tab 错误显示趋势内容（延迟加载索引错位）",
    ],
  },
  {
    version: "v6.1.0",
    date: "2026.07.01",
    tag: "",
    changes: [
      "启动速度优化：非首屏 Tab 延迟加载，启动只构建今日",
      "趋势图 QPixmap 缓存：数据不变时直接复用，避免重绘",
      "飞书日程手动刷新按钮、AI 报告强制刷新按钮",
      "复盘记忆上次选择的学科和标签",
      "护眼提醒浮窗加跳过按钮",
    ],
  },
  {
    version: "v6.0.2",
    date: "2026.07.01",
    tag: "",
    changes: [
      "成就静默解锁：启动时自动检查历史数据，解锁已达标成就",
      "飞书日程改为每天获取一次（原 5 分钟），减少 99% 调用",
      "失败重试机制：10 分钟后重试，最多 3 次",
    ],
  },
  {
    version: "v6.0.1",
    date: "2026.07.01",
    tag: "",
    changes: [
      "修复飞书日程 GBK 解码失败（subprocess encoding=utf-8）",
      "浮球 popup 日程简写格式",
    ],
  },
  {
    version: "v6.0.0",
    date: "2026.06.30",
    tag: "",
    changes: [
      "主界面去置顶：不再永远挡在最前（对标正常产品）",
      "AI 服务自定义提供商：支持任何 OpenAI 兼容 API",
      "内置免费 AI（Cloudflare 代理）：key 隐藏在 CF secrets",
      "每 IP 每天 30 次限流 + model 白名单 + 多上游 fallback",
    ],
  },
  {
    version: "v5.9.0",
    date: "2026.06.30",
    tag: "",
    changes: [
      "AI 报告错误信息透明化：显示每个服务的具体错误",
      "成就扩充：16 → 19 个（新增一周巅峰/月度学霸/反思大师）",
      "成就进度条修复：QProgressBar 自适应，百分比显示，差额提示",
      "今日解锁成就加金色边框高亮，Toast 延长至 8 秒",
    ],
  },
  {
    version: "v5.8.0",
    date: "2026.06.30",
    tag: "",
    changes: [
      "GitHub 私有仓库自动备份：每 24 小时备份学习/复盘/设置/打卡/历史数据",
      "设置页新增备份区块：验证连接 / 立即备份 / 一键恢复",
      "官网 Footer 去重、文档页优化、修复视频路径 404",
    ],
  },
  {
    version: "v5.7.0",
    date: "2026.06.30",
    tag: "",
    changes: [
      "浮球重绘：矢量闪电图标 + 径向渐变底 + 琥珀渐变进度环",
      "侧边栏 logo 矢量化，消除 emoji 依赖",
      "主题系统修复：light 主题真正生效（主界面 + popup 全链路）",
      "空状态设计：新用户引导文案（趋势图/AI报告/复盘）",
      "info popup 跟随主题变色",
    ],
  },
  {
    version: "v5.6.0",
    date: "2026.06.30",
    tag: "",
    changes: [
      "成就显示优化：卡片式展示+进度条+每个成就当前进度文本",
      "环境白噪音优化：30秒循环(原10秒)、首尾crossfade消除断裂、批量写入性能提升",
      "邮件周报改用Agent QQ邮箱(agently-cli)，移除SMTP配置",
      "关于界面字体放大(11px→13px)，环境/数据/AI服务信息清晰可见",
    ],
  },
  {
    version: "v5.5.0",
    date: "2026.06.29",
    tag: "",
    changes: [
      "成就/徽章系统：16个成就解锁Toast通知，关于页集中展示",
      "GitHub风格学习热力图：52周×7天，5级颜色梯度",
      "环境白噪音：5种程序生成音效，独立音量控制",
      "每周邮件周报：SMTP配置，HTML格式AI报告，周一自动发送",
      "主题切换：深色/浅色/跟随系统，设置页选择",
      "全局快捷键：Ctrl+Alt+P/S/B，Ctrl+1~5切换Tab",
      "API Key加密存储：XOR+base64+机器盐值",
    ],
  },
  {
    version: "v5.4.0",
    date: "2026.06.29",
    tag: "",
    changes: [
      "飞书日程集成：实时显示当前/下一个日程，每5分钟自动刷新",
      "趋势时间选择器：近7/14/30天 + 自定义日期范围",
      "AI API Key 配置界面：设置 tab 直接输入 SenseNova / Agnes Key",
      "修复 SenseNova 推理模型 content 为空、任务栏图标丢失、多实例启动竞态",
      "「关于」「趋势」页面重新设计，视觉更精致",
    ],
  },
  {
    version: "v5.1",
    date: "2026.06.26",
    tag: "",
    changes: [
      "主界面全面实时刷新：学习时长/轮次/休息时长/状态/倒计时每秒更新",
      "AI 报告大幅升级：max_tokens 2048、prompt 充实（含复盘明细）、字数 400+、5 章节深度分析",
      "AI 不可用时自动降级为本地数据摘要报告，不再空白",
      "修复复盘摘要空列表崩溃、连续打卡恢复逻辑、月趋势越界、季年统计错误",
      "删除死代码，移除失效窗口按钮",
    ],
  },
  {
    version: "v5.0",
    date: "2026.06.25",
    tag: "",
    changes: [
      "柱状图悬浮提示：鼠标移到趋势分析柱子即可看到具体学习时长",
      "复盘学科新增「其他」选项，支持健身/阅读/考试等非学科场景",
      "AI 报告后台线程（QThread 异步），不再阻塞 UI",
      "修复 AI 报告卡死、StatsWindow tooltip 不显示、PyQt5 sip 导入兼容性等 P0 bug",
      "趋势分析全面重构：移除电脑使用时长，改为纯学习时长单柱图",
      "浮球图标改为 ⚡ 闪电符号",
    ],
  },
  {
    version: "v4.4",
    date: "2026.06.23",
    tag: "",
    changes: [
      "5 标签页主界面（今日/AI报告/趋势/设置/关于）",
      "⚡ 浮球独立（60×60）、点击弹出信息面板",
      "20-20-20 护眼浮窗、热力图、B站收藏夹",
      "开源发布：移除 Pro 订阅系统，MIT 协议全部免费",
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
