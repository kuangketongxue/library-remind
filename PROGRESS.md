# 休息提醒项目 — 进度记录

> 保存时间：2026-06-18
> 目的：记录当前完成状态，方便后续继续

---

## 一、已完成 ✅

### 1. 看门狗移除
- **watchdog.py**（主版 + Pro版）已删除
- **注册表自启动**已更新：指向 `rest_reminder.py --silent`，不再指向 watchdog.py
- **`os._exit(1)` 修复**：改为 `sys.exit(1)`，正常走 atexit 清理
- 所有文档已更新：AGENTS.md、CLAUDE.md、README.md、一键安装.bat、卸载.bat

### 2. 搜索规则记录
- **`experience-search-mandatory-all-sources.md`**：完整指南已保存
- **`experiences/REFERENCE.md`**：搜索分类已添加索引
- **`MEMORY.md`**：本次新增已添加
- 规则要点：5源并行（zhihu + global + tavily×1 + firecrawl-keyless + opencli小红书）

### 3. FloatingBall 右键菜单 ✅
- **左键点击**：显示/隐藏主界面
- **右键菜单**：🖥️ 打开主界面、🌐 打开官方网站、✕ 退出
- 修改文件：`rest_reminder.py` class FloatingBall

### 4. 主界面卡片化 ✅
- **样式**：深黑背景 `#08080c`、毛玻璃卡片 `rgba(20,20,24,0.85)`、金色边框 `#d4af37`
- **布局**：顶部（品牌 + 计时器 + 关闭）→ 2×2 卡片网格 → 按钮区
- **卡片内容**：
  - 📚 今日产出（学习h + 进度条）
  - 🔥 连续打卡（天数）
  - ☕ 今日休息（分钟）
  - ⏳ 22:00倒计时（倒计时 + 进度条）
- **按钮**：▶ 开始学习、⏸ 暂停
- **移除**：大计时器、进度条、分隔线、电脑使用行、电池行、退出按钮
- 后台电池监控和电脑使用追踪保留，只是 UI 不再显示
- 语法检查通过 ✅

### 5. Netlify 清理 ✅
- 删除 `netlify.toml`、`@netlify/plugin-nextjs` 依赖
- 官网链接全部改为 Cloudflare Pages

### 6. 设计稿（HTML mockup）
- 文件：`~/Desktop/休息提醒/ui-mockup.html`
- 预览：`~/Desktop/休息提醒/ui-preview-v3.png`

---

## 二、未完成 ⏳

### 7. 官网 Clerk 登录
- **依赖**：`@clerk/nextjs` 已在 package.json
- **需要配置的文件**：
  ```typescript
  // src/app/layout.tsx
  import { ClerkProvider } from '@clerk/nextjs'
  ```
- **API Key**：
  ```
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YWJzb2x1dGUtymFzcy04Ni5jbGVyay5hY2NvdW50cy5kZXYk
  CLERK_SECRET_KEY=sk_test_adzAQSazf24tWDHWofs0ZMiUAB4s3j09CtvsfrVT0M
  ```
- **文件路径**：`~/Desktop/休息提醒/rest-reminder-site/`
- **状态**：`layout.tsx` 和 `page.tsx` 尚未配置 ClerkProvider。Read 工具因中文路径问题无法直接读取，需用 Python 或 Bash 操作

### 8. Pro 版 AI 功能（GLM API）
- **API**：
  ```
  URL: https://open.bigmodel.cn/api/anthropic
  Key: 6890794e3ec14a1fa56347638f2e6e82.5A1zOJFpwtUETmuD
  模型: glm-4.6v-flash
  ```
- **需要创建的文件**：`~/Desktop/休息提醒/rest-reminder-pro/ai_features.py`
  - `analyze_study_data()` — 分析学习数据
  - `generate_weekly_report()` — 周报生成
  - `generate_monthly_report()` — 月报生成
  - `generate_quarterly_report()` — 季报生成
- **Pro 验证**：通过 Clerk userId（用户在后台手动标记 Pro）

### 9. 注册表自启动状态
- 当前注册表指向：`rest_reminder.py --silent` ✅ 已更新
- 但程序尚未重启验证

### 10. RestReminder.spec 打包配置
- 需要更新以移除 watchdog.py 引用
- Pro版相关配置也需更新

---

## 三、文件修改清单

| 文件 | 改动 |
|------|------|
| `rest_reminder.py` | init_ui 卡片化、FloatingBall 右键菜单、os._exit→sys.exit、注册表指向、progress_bar/battery/goal 引用移除 |
| `rest-reminder-pro/rest_reminder.py` | 注册表指向 |
| `watchdog.py` | **已删除** |
| `rest-reminder-pro/watchdog.py` | **已删除** |
| `AGENTS.md` | 移除看门狗 |
| `CLAUDE.md` | 移除看门狗 |
| `README.md` | 移除看门狗 + Netlify链接改CF |
| `一键安装.bat` | 移除看门狗 |
| `卸载.bat` | 移除看门狗 |
| `版本记录.md` | 新增 v4.0 记录 |
| `marketing/xhs/xhs-05-download.html` | 官网链接改CF |
| `rest-reminder-site/DISTRIBUTION.md` | 官网链接改CF |
| `rest-reminder-site/public/theme-readme.md` | 官网链接改CF |
| `rest-reminder-site/src/components/Footer.tsx` | 移除 Netlify 赞助商 |
| `rest-reminder-site/src/components/Sponsors.tsx` | 移除 Netlify 赞助商 |
| `rest-reminder-site/package.json` | 移除 @netlify/plugin-nextjs |
| `rest-reminder-site/netlify.toml` | **已删除** |
| `rest-reminder-pro/一键安装.bat` | 移除看门狗 |
| `rest-reminder-pro/卸载.bat` | 移除看门狗 |
| `rest-reminder-pro/RELEASE_NOTES.md` | 移除看门狗 |

---

## 四、需要解决的问题

1. **中文路径问题**：`~/.claude/skills/zhihu-search/scripts/zhihu-search.py` 和 `rest-reminder-site/` 等带有中文名的路径在 Bash/PowerShell 下编码混乱，需用 Python 操作
2. **程序重启**：修改代码后需杀掉旧进程再启动新程序
3. **Pro 版验证逻辑**：需要从 Supabase 迁移到 Clerk
4. **Pricing 页面**：官网定价需更新（Pro = AI功能，不是自定义个性化）

---

## 五、关键技术配置

### Clerk
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YWJzb2x1dGUtymFzcy04Ni5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_SECRET_KEY=sk_test_adzAQSazf24tWDHWofs0ZMiUAB4s3j09CtvsfrVT0M
```

### Supabase
```
NEXT_PUBLIC_SUPABASE_URL=https://uodetuzjixttlscysfll.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_hhjn2zMREPKrj6uRU-dOJA_UG671yW9
DATABASE_URL=postgresql://postgres.uodetuzjixttlscysfll:Bd5h88MDLBfaEiFg@aws-1-us-east-2.pooler.supabase.com:6543/postgres?pgbouncer=true
DIRECT_URL=postgresql://postgres.uodetuzjixttlscysfll:Bd5h88MDLBfaEiFg@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

### GLM AI API
```
URL: https://open.bigmodel.cn/api/anthropic
Key: 6890794e3ec14a1fa56347638f2e6e82.5A1zOJFpwtUETmuD
Model: glm-4.6v-flash
```

### 搜索工具
```
zhihu-search:    python3 ~/.claude/skills/zhihu-search/scripts/zhihu-search.py
global-search:   python3 ~/.claude/skills/global-search/scripts/global-search.py
tavily-1:        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（主key）
tavily-2:        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（备用key）
firecrawl:       https://api.firecrawl.dev/v2/search（keyless）
小红书:           opencli xiaohongshu search
```

---

## 六、下次续接

**推荐执行顺序**：
1. 配置官网 Clerk（layout.tsx + page.tsx）
2. 创建 AI 功能文件（ai_features.py）
3. 更新 Pro 版验证逻辑（Clerk → Supabase）
4. 更新官网定价页
5. 重启程序验证所有修改