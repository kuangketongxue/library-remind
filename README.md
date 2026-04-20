# 休息提醒挂件

这是一个固定在屏幕右侧的提醒挂件，支持隐藏和展开。

它会做这些事：
- 提醒时段：每天 04:30 到 23:00
- 连续使用电脑 1 小时：提醒你休息，并自动打开眼保健操视频
- 电脑没有充上电：会立刻弹出提醒；如果一直没插电，会按间隔再次提醒
- 每天 23:00：提醒你准备睡觉，23:01 之后不再补发
- 每次提醒都会有铃声
- 提醒可以手动点“知道了”
- 不会锁屏，也不会强制你停下手头工作

## 安装开机自启

```powershell
python .\break_reminder.py --install-autostart
```

看到 `autostart installed (...)` 就表示成功。

## 启动挂件

```powershell
python .\break_reminder.py
```

默认会自动转为后台运行，所以关掉这个终端后，挂件也会继续运行。

## 快速测试

测试模式下，连续使用 30 秒就会触发休息提醒：

```powershell
python .\break_reminder.py --test-mode
```

单独预览“没插电提醒”弹窗：

```powershell
python .\break_reminder.py --demo-alert power
```

## 逻辑自测

```powershell
python .\break_reminder.py --self-test
```

看到 `self-test passed` 说明核心判断通过。

## 常驻说明

- 只需要手动启动一次，程序会自动确保开机登录后继续启动
- 程序会避免重复启动多个挂件
