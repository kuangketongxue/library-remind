## 🎯 主界面文字乱码修复（Hotfix）
**根因**：9 处 `QFont()` 调用把 CSS 风格逗号分隔串（如 `'Georgia, "Noto Serif SC", serif'` 或 `'Consolas, "SF Mono", monospace'`）当作字体名单名字传入。QFont 不认识这种分隔，整个字符串匹配失败回退到系统默认字体 → 中文字符 moji-bake / 方块 / emoji 不渲染。

**修复**：所有 `QFont` 调用改为只用单一主字体名（`Georgia` / `Consolas` / `Microsoft YaHei` / `Segoe UI Emoji`），fallback 留给 Qt 字体链接表自动处理。

## 🔧 修复飞书日历 lark-cli 路径亡址
WorkBuddy 已删但 `.settings.json` 里 `lark_cli_path` 仍指向亡址 → 改为 npm 全局路径 `C:\Users\binlo\AppData\Roaming\npm\lark-cli.cmd`（v1.0.65 可用）。

## 🤖 AI 服务超时 fallback 修复
内置 Cloudflare Worker 代理在大陆经常 30 秒超时 → `_call_ai()` 所有上游失败时从本地 `.wisdom_quotes.json`（9 条狂客智慧语录）fallback 一条内容继续显示。超时不再显示错误 toast，review 报告始终可用。

## 🎬 官网 Hero 视频修复
- 加 `poster="/hero-banner.png"` → 视频未缓冲完时显示主图
- `<video>` 重写：`preload="auto"` + `opacity: 0→1 onCanPlay` + `onError=display:none`
- 加 CSS radial-gradient fallback → 万一视频加载失败不黑屏
- 4 个法律页面现有内容 + 1 处成就数量 bug 修（19→17）

## 📄 官网新增法律合规页面
新增 4 个独立页面：pricing / privacy / rules / terms，含实质性内容（隐私政策、MIT 协议、Issue/PR 规范、定价说明）。

## 📚 文档刷新
- CHANGELOG.md 首部新增 v6.2.0 节点 + 保留历史结构
- README.md / README.zh.md 英/中：新增功能（Feishu Calendar / Achievements + Streaks 17 badges / Email Report / GitHub Backup）+ 文件结构新增 `feishu_calendar.py` / `backup.py`
- 主程序 `VERSION = 'v6.2.0'` 同步
