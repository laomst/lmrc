# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个模块化的 PowerShell 环境配置框架（lmrc/powershell），通过在 PowerShell Profile 中 `. <项目目录>\index.ps1` 加载。所有文件均为纯 PowerShell 脚本，无构建/测试/lint 流程。

## 架构

### 加载流程（index.ps1 六阶段）

`index.ps1` 是入口，按固定顺序加载配置，每个核心模块前后都有 hook 点（通过 `includes.ini` 配置）：

1. **pre_export** → `exports.ps1`（环境变量）→ **post_export**
2. **pre_path** → `path.ps1`（PATH 配置）→ **post_path**
3. **pre_function** → `function.ps1`（函数加载器）→ **post_function**
4. **pre_alias** → `alias.ps1`（别名）→ **post_alias**
5. **pre_completion** → `completion.ps1`（补全）→ **post_completion**
6. **pre_prompt** → `prompt.ps1`（提示符）→ **post_prompt**

之后加载根目录下剩余的 `*.ps1` 文件（跳过已加载的），最后执行 `post_all`。加载完成后清理所有临时变量和工具函数。

### includes.ini 扩展机制

- `includes.ini` 是机器相关的配置（不应提交），`includes_example.ini` 是模板
- INI 格式：`[section_name]` 下列出绝对路径，每行一个脚本
- 仅支持绝对路径（盘符 `C:\`、UNC `\\`、`~` 或 `$` 开头）
- 解析逻辑在 `includes/02-loader.ps1`，提供 `Load-LmrcScript` 和 `Load-LmrcSection` 两个工具函数

### 目录结构

- `functions/` — 按编号分类的工具函数（01-fs 等），由 `function.ps1` 自动加载目录下所有 `*.ps1`
- `includes/` — 预加载模块（公共工具函数、INI 解析器），由 `include.ps1` 在 index.ps1 最开始加载

## 编码约定

- 注释使用中文
- 函数文件按 `NN-category.ps1` 编号命名
- 使用 `$script:` 作用域声明框架内部变量
- 工具函数使用 `Lmrc` 前缀避免与系统命令冲突（如 `Load-LmrcScript`）
- 加载完成后通过 `Remove-Variable` 和 `Remove-Item Function:` 清理临时变量和函数
