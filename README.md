# lmrc

个人工具集仓库，包含多个独立子项目，用于统一管理跨平台的开发环境配置和效率工具。

## 子项目

| 子项目 | 简介 | macOS | Linux | Windows |
|--------|------|:-----:|:-----:|:-------:|
| [zsh](zsh/) | 模块化 zsh 环境配置框架 | ✅ | ✅ | ❌ |
| [typora-watch-dog](typora-watch-dog/) | Typora Markdown 工作区文件监控服务 | ✅ | ✅ | ✅ |
| [typora-themes](typora-themes/) | Typora 自定义主题（vue-laomst 亮色/暗色） | ✅ | ✅ | ✅ |
| [auto-hot-key](auto-hot-key/) | 模拟 macOS 键盘习惯的映射脚本 | ❌ | ❌ | ✅ |
| [powershell](powershell/) | PowerShell 配置 | ❌ | ❌ | ✅ |

### 平台说明

- **zsh** — 依赖 zsh，适用于所有支持 zsh 的 Unix-like 系统
- **typora-watch-dog** — Python 3 编写，跨平台运行；系统服务安装方式因平台而异：Linux 使用 systemd，macOS 使用 launchd，Windows 使用 NSSM
- **typora-themes** — 纯 CSS 主题，跟随 Typora 支持的所有平台
- **auto-hot-key** — 基于 AutoHotkey v2，仅限 Windows

各子项目均有独立的 README.md，包含详细的安装和使用说明。
