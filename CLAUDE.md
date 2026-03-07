# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

lmrc 是一个个人工具集仓库（monorepo），包含多个独立子项目，用于统一管理跨平台的开发环境配置和效率工具。所有子项目共享同一个 Git 仓库，但彼此独立，无交叉依赖。

## 子项目

| 子项目 | 技术栈 | 用途 |
|--------|--------|------|
| `zsh/` | Zsh 脚本 | 模块化 zsh 环境配置框架（环境变量、PATH、函数、别名、补全、提示符） |
| `typora-watch-dog/` | Python 3 + watchdog | Typora Markdown 工作区文件监控服务，自动管理 front matter 和文件索引 |
| `typora-themes/` | 纯 CSS | Typora 自定义主题（vue-laomst 亮色/暗色） |
| `auto-hot-key/` | AutoHotkey v2 | Windows 上模拟 macOS 键盘习惯的映射脚本 |
| `powershell/` | PowerShell | 模块化 PowerShell 环境配置框架，与 `zsh/` 对等设计 |

每个子项目有自己的 CLAUDE.md 和 README.md，包含详细的架构和开发指导。处理某个子项目时，优先参考其自身的 CLAUDE.md。

## 常用命令

### typora-watch-dog（唯一需要运行环境的子项目）

```bash
cd typora-watch-dog

# 环境准备
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# 启动监控
python src/watch_workspace.py -w <workspace_path>

# 守护进程
python src/watch_workspace.py -d
python src/watch_workspace.py --stop
python src/watch_workspace.py --status

# 验证索引
python src/watch_workspace.py --verify-index
```

其余子项目（zsh、typora-themes、auto-hot-key）无构建/测试/lint 流程，直接编辑源文件即可。

## 编码约定

- 注释和文档使用中文
- zsh 脚本：函数文件按 `NN-category.zsh` 编号命名，使用 `typeset -g` 声明全局变量
- Python（typora-watch-dog）：依赖仅 `watchdog>=4.0.0`，模块单向依赖 `watch_workspace.py` → `index_typora_markdowns.py` → `move_assets_to_root_url.py`
- CSS（typora-themes）：所有颜色通过 CSS 变量定义，暗色主题通过覆盖变量实现
- AutoHotkey：使用 v2 语法（`#Requires AutoHotkey v2.0`）

## .gitignore 要点

- `zsh/includes.ini` 是机器相关配置，不提交（模板为 `includes_example.ini`）
