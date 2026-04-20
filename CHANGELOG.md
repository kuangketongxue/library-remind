# 休息提醒应用 更新日志

## v1.5-stable (2026-04-21)
### 改进
- 删除"退出"按钮，强制应用持续运行
- 删除托盘图标右键菜单中的"退出"选项
- 用户无法通过任何方式退出应用，只能最小化到托盘
- 点击窗口关闭按钮（X）会自动隐藏到托盘，不会退出

## v1.4-stable (2026-04-21)
### 修复
- 修复乱码/问号问题，恢复所有中文显示
  - 音频异常提示：`声音/麦克风异常：{problem_signature}`
  - 状态提示：`状态：音频异常`
  - 弹窗标题：`音频设备异常`
  - 正常状态恢复：`状态：正常`
  - 音频设备恢复：`音频设备已恢复正常。`
- 增加窗口大小从 350×350 到 420×450，确保所有内容完整显示
- 调整文字折行长度从 320 到 390

## v1.3-stable (2026-04-21)
### 改进
- 添加托盘图标自动恢复机制
  - 每30秒检查托盘图标状态
  - 如果图标消失，自动重新添加
  - 添加 `check_and_restore()` 方法
- 改进开机自启动功能
  - 三重启动保障：注册表 + VBS启动文件 + BAT启动文件
  - 确保重启电脑后应用能正常自动启动

## v1.2-stable (2026-04-21)
### 新增
- 完整系统托盘图标功能
  - 初始化 TrayIconController
  - 左键点击恢复窗口
  - 右键点击显示菜单（恢复/退出）
  - 在任务栏右下角系统托盘区域显示图标
  - 图标自动清理和资源管理

## v1.1-stable (2026-04-21)
### 修复
- 修复窗口大小问题，调整为合适尺寸
- 确保隐藏后不会强制弹出
  - 修改 `_visibility_guard_tick` 方法，当 `is_collapsed` 为 True 时直接返回
- 添加互斥体释放逻辑，避免资源泄漏
- 添加临时图标文件清理功能
- 确保单实例检查在所有模式下正常工作

## v1.0-stable (2026-04-21)
### 初始版本
- 核心功能
  - 电脑每1小时自动打开B站视频
  - 23点提醒睡觉
  - 检测充电状态并在未充电时提醒
- 系统托盘最小化
- 音频设备健康监控
- 休息提醒弹窗
- 开机自启动配置
- 单实例运行保护

---

## 版本切换命令

```bash
# 查看所有版本标签
git tag -l

# 切换到最新稳定版本
git checkout v1.4-stable

# 切换到特定版本
git checkout v1.3-stable
git checkout v1.2-stable
git checkout v1.1-stable
git checkout v1.0-stable

# 查看当前版本
git log --oneline -10
```

## 常用命令

```bash
# 运行应用
python break_reminder.py

# 测试模式运行（15秒后自动退出）
python break_reminder.py --test-mode --smoke-seconds=15

# 运行自检
python break_reminder.py --self-test

# 查看电源状态
python break_reminder.py --power-status

# 手动安装开机自启动
python break_reminder.py --install-autostart
```

---

最后更新：2026-04-21
