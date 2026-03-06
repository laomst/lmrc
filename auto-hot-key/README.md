# AutoHotkey macOS 键盘习惯映射

在 Windows 上模拟 macOS 键盘操作习惯的 AutoHotkey v2 脚本，适合长期使用 macOS 后切换到 Windows 的用户。

## 环境要求

- Windows 系统
- [AutoHotkey v2.0+](https://www.autohotkey.com/download/)

## 使用方法

### 编译为可执行文件

推荐使用 AutoHotkey 自带的 [Ahk2Exe](https://www.autohotkey.com/docs/v2/Scripts.htm#ahk2exe) 编译器将脚本编译为独立的 `.exe` 文件，编译后运行无需安装 AutoHotkey。

1. 安装 AutoHotkey v2（安装包中已包含 Ahk2Exe）
2. 右键 `laomst-ahk-script.ahk` → **Compile Script**
3. 生成的 `laomst-ahk-script.exe` 即可独立运行

也可通过命令行编译：

```cmd
Ahk2Exe.exe /in laomst-ahk-script.ahk /out laomst-ahk-script.exe
```

### 开机自启

将编译好的 `laomst-ahk-script.exe`（或 `.ahk` 脚本）的快捷方式放入启动文件夹：

```
Win + R → 输入 shell:startup → 回车
```

将快捷方式粘贴到打开的文件夹中即可。

## 功能说明

### NumLock 常开

NumLock 始终保持开启状态，避免小键盘数字键失效。

### 行首/行尾导航

| 按键 | 映射为 | 效果 |
|------|--------|------|
| `PgUp` | `Home` | 跳转到行首 |
| `PgDn` | `End` | 跳转到行尾 |

### 模拟 macOS 快捷键

使用 `Alt` 键模拟 macOS 的 `Cmd` 键行为：

| 按键 | 映射为 | 功能 |
|------|--------|------|
| `Alt + C` | `Ctrl + Insert` | 复制 |
| `Alt + V` | `Shift + Insert` | 粘贴 |
| `Alt + X` | `Ctrl + X` | 剪切 |
| `Alt + Z` | `Ctrl + Z` | 撤销 |
| `Alt + A` | `Ctrl + A` | 全选 |
| `Alt + S` | `Ctrl + S` | 保存 |

> 复制和粘贴使用 `Insert` 组合键而非 `Ctrl+C/V`，是为了避免与终端中的快捷键冲突。

### CapsLock 防误触

CapsLock 需**长按 0.5 秒**才会切换大小写状态，轻触不生效。

同时处理了以下修饰键组合场景，防止在快速输入时意外切换大小写：

- `Alt + CapsLock`
- `Ctrl + CapsLock`
- `Shift + CapsLock`
