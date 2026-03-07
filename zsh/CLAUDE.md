# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个模块化的 zsh 环境配置框架（lmrc/zsh），通过在 `~/.zshrc` 中 `source <项目目录>/index.zsh` 加载。所有文件均为纯 zsh 脚本，无构建/测试/lint 流程。

## 架构

### 加载流程（index.zsh 六阶段）

`index.zsh` 是入口，按固定顺序加载配置，每个核心模块前后都有 hook 点（通过 `includes.ini` 配置）：

1. **pre_export** → `exports.zsh`（环境变量）→ **post_export**
2. **pre_path** → `path.zsh`（PATH 配置）→ **post_path**
3. **pre_function** → `function.zsh`（函数加载器）→ **post_function**
4. **pre_alias** → `alias.zsh`（别名）→ **post_alias**
5. **pre_completion** → `completion.zsh`（补全）→ **post_completion**
6. **pre_prompt** → `prompt.zsh`（提示符）→ **post_prompt**

之后加载根目录下剩余的 `*.zsh` 文件（跳过已加载的），最后执行 `post_all`。加载完成后清理所有临时变量和工具函数。

### includes.ini 扩展机制

- `includes.ini` 是机器相关的配置（不应提交），`includes_example.ini` 是模板
- INI 格式：`[section_name]` 下列出绝对路径，每行一个脚本
- 支持 `~` 和 `$HOME` 展开，不存在的文件静默跳过
- 解析逻辑在 `includes/02-loader.zsh`，提供 `load_script()` 和 `load_section()` 两个工具函数

### 目录结构

- `functions/` — 按编号分类的工具函数（01-fs, 02-network, 03-git 等），由 `function.zsh` 自动加载目录下所有 `*.zsh`
- `includes/` — 预加载模块（公共工具函数、INI 解析器、prompt-select 交互菜单），由 `include.zsh` 在 index.zsh 最开始加载

## 编码约定

- 所有脚本使用 `#!/bin/zsh` shebang
- 函数文件按 `NN-category.zsh` 编号命名
- 使用 `typeset -g` 声明全局变量，`setopt LOCAL_OPTIONS` 限制选项作用域
- 注释使用中文
