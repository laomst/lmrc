# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## ⚠️ 重要：项目必须位于用户家目录

**本项目必须放置在用户家目录 (`~`) 下，或通过符号链接指向 `~/lmrc` 才能正常使用！**

### 正确的安装方式

```bash
# 方式一：直接放置在家目录（推荐）
cd ~
git clone <repository-url> lmrc

# 方式二：使用符号链接
ln -s ~/Projects/lmrc ~/lmrc
```

**原因：** 配置文件中硬编码了 `~/lmrc` 路径引用，如 `source ~/lmrc/index.sh`。

---

## 仓库概述

这是一个个人配置工具仓库 `lmrc` (Laomst's RC)，包含三个主要部分：

1. **`bash/`** - Bash Shell 配置（仅限 Linux/macOS）
2. **`zsh/`** - Zsh Shell 配置（仅限 Linux/macOS）
3. **`typora/`** - Typora Markdown 编辑器扩展工具（跨平台）

> **注意：** Windows 用户请使用 WSL (Windows Subsystem for Linux) 或等待后续的 PowerShell 配置支持。

---

## 第一部分：Shell 配置 (bash/ & zsh/)

### 目录结构

```
lmrc/
├── bash/
│   ├── index.sh      # Bash 入口文件
│   ├── exports.sh    # 本地环境变量配置（不提交到仓库）
│   ├── path.sh       # PATH 和 SDK 路径配置
│   ├── function.sh   # 自定义工具函数
│   ├── alias.sh      # 命令别名
│   ├── completion.sh # Shell 自动补全
│   └── prompt.sh     # 提示符定制
└── zsh/
    ├── index.zsh     # Zsh 入口文件
    ├── exports.zsh   # 本地环境变量配置（不提交到仓库）
    ├── path.zsh      # PATH 和 SDK 路径配置（Java、Maven、Python）
    ├── function.zsh  # 自定义工具函数
    ├── alias.zsh     # 命令别名
    ├── completion.zsh # Shell 自动补全
    ├── prompt.zsh    # 自定义提示符（含 git 状态）
    └── claude.zsh    # Claude Code 模型切换函数
```

### 安装方式

**Bash 配置：** 在 `~/.bashrc` (Linux/WSL) 或 `~/.bash_profile` (macOS) 中添加：
```bash
source ~/lmrc/bash/index.sh
```

**Zsh 配置：** 在 `~/.zshrc` 中添加：
```bash
source ~/lmrc/zsh/index.zsh
```

### 平台支持

| Shell | Linux | macOS | Windows | WSL |
|-------|-------|-------|---------|-----|
| Bash  | ✅    | ✅    | ❌      | ✅  |
| Zsh   | ✅    | ✅    | ❌      | ✅  |

**Windows 用户：** 请使用 WSL 安装 Linux 发行版（如 Ubuntu）来使用这些配置。纯 Windows PowerShell 配置正在计划中。

### 本地环境变量配置

`exports.sh` (Bash) 和 `exports.zsh` (Zsh) 用于存放个人环境变量配置，如 API keys、本地路径等敏感信息。

- 这两个文件**不提交到 Git 仓库**（已在 .gitignore 中排除）
- 文件不存在时不会报错，可按需创建
- 在所有其他配置文件**之前**加载，确保变量可用

示例 `exports.zsh`:
```zsh
# API Keys
export OPENAI_API_KEY="sk-xxx"
export ANTHROPIC_API_KEY="sk-ant-xxx"

# 本地路径
export MY_PROJECTS="$HOME/Projects"
```

### 加载顺序

Zsh 配置文件按以下顺序加载：
1. `exports.zsh` - 本地环境变量（优先加载，如果文件存在）
2. `path.zsh` - PATH 和 SDK 变量
3. `function.zsh` - 自定义函数
4. `alias.zsh` - 命令别名
5. `completion.zsh` - 自动补全
6. `prompt.zsh` - 提示符定制
7. `claude.zsh` - 模型切换函数
8. 其他 `.zsh` 文件（自动发现并加载，排除已加载的文件）

Bash 配置文件加载顺序类似：
1. `exports.sh` - 本地环境变量（优先加载，如果文件存在）
2. `path.sh`、`function.sh` 等按 CONFIG_FILES 顺序加载
3. 其他 `.sh` 文件（自动发现并加载，排除已加载的文件）

### Claude Code 模型切换器

`zsh/claude.zsh` 定义了包装函数，在启动 `claude` 前为不同的 LLM 提供商设置环境变量。每个函数在执行前会验证所需的 API 密钥。

可用函数：
- `claude-glm` - 使用 GLM (智谱 AI) 模型
- `claude-minimax` - 使用 MiniMax 模型

示例：
```zsh
claude-glm "帮我写一个函数"
```

这些函数设置的环境变量会被子进程继承，包括 Claude Code 启动的任何 sub-agent。

### SDK 配置

SDK 路径在 `zsh/path.zsh` 中配置：
- `SDK_HOME_DIR="/Library"` - SDK 基础目录
- `JAVA_HOME`、`JAVA8_HOME`、`JAVA21_HOME` - Java 版本
- `MAVEN_HOME` - Maven 位置
- `PYTHON_HOME` - Python 框架路径

### 自定义路径管理

`path.sh/path.zsh` 会将 `CUSTOM_PATHS` 数组中定义的路径添加到 PATH 前面，并导出 `LMRC_PATH` 环境变量：

- `LMRC_PATH` - 包含所有由 lmrc 添加的自定义路径
- 数组靠前的元素优先级更高（最先被添加到 PATH）

### 工具函数：pathls

`pathls` 函数用于显示 PATH 列表：

```bash
# 显示完整 PATH（每行一个）
pathls

# 分块显示 LMRC_PATH 和 PATH
pathls -i
```

---

## 第二部分：Typora 扩展工具 (typora/)

### 目录结构

```
typora/
├── scripts/                    # Python 工具脚本
│   ├── index_typora_markdowns.py   # Markdown 文件索引
│   ├── watch_workspace.py          # 文件监控服务
│   ├── move_assets_to_root_url.py  # 资源移动工具
│   ├── install-service.sh          # 服务安装脚本
│   └── util/                       # 工具模块
│       ├── __init__.py
│       ├── indexer.py              # 索引核心逻辑
│       ├── front_matter.py         # Front matter 处理
│       └── logger.py               # 日志配置
├── themes/                     # Typora CSS 主题
│   ├── vue-laomst/             # 亮色主题（模块化 CSS）
│   └── vue-laomst-dark/        # 暗色主题
├── key_mappings/               # 快捷键配置
│   └── key-mapping-windows.json
└── service-install/            # 服务安装文档
    ├── README.md
    └── windows-nssm.md
```

### 脚本使用

#### index_typora_markdowns.py - 索引管理

为 Markdown 文件添加 YAML front matter 并维护索引文件。

**生成的 front matter：**
```yaml
---
article-id: a1b2c3d4
typora-root-url: ../
typora-copy-images-to: ../assets
---
```

**索引文件结构** (`.index.json`)：
```json
{
  "article-id": "/相对路径/文件.md"
}
```

```bash
# 处理单个文件
python typora/scripts/index_typora_markdowns.py path/to/file.md

# 处理目录
python typora/scripts/index_typora_markdowns.py path/to/directory

# 指定工作空间路径
python typora/scripts/index_typora_markdowns.py -w /path/to/workspace path/to/file.md
```

#### watch_workspace.py - 文件监控服务

自动监控工作空间中的 Markdown 文件变化，实时更新索引。

**监控事件处理：**
| 事件 | 处理 |
|------|------|
| 新建 | 自动添加 front matter 和索引 |
| 移动 | 自动更新索引路径 |
| 删除 | 自动从索引移除 |
| 修改 | 检查并更新（带防抖） |

```bash
# 前台运行
export TYPORA_WORKSPACE=/path/to/workspace
python typora/scripts/watch_workspace.py

# 后台运行
python typora/scripts/watch_workspace.py --daemon

# 停止服务
python typora/scripts/watch_workspace.py --stop

# 查看状态
python typora/scripts/watch_workspace.py --status

# 验证并修复索引（不启动监控）
python typora/scripts/watch_workspace.py --verify-index

# 清理旧日志（默认保留 30 天）
python typora/scripts/watch_workspace.py --clean-logs
```

**安装为系统服务：**
```bash
# macOS/Linux (LaunchAgent/systemd)
sudo typora/scripts/install-service.sh install

# 管理服务
./typora/scripts/install-service.sh {start|stop|restart|status|logs|uninstall}
```

**日志配置：**
- 日志目录：`~/.typora-ext-logs/`
- 按日期命名：`typora-watch-YYYY-MM-DD.log`
- 默认保留 30 天，自动清理
- 查看日志：`tail -f ~/.typora-ext-logs/typora-watch-*.log`

**依赖：**
- Python 3.7+
- watchdog (`pip install watchdog`)

### Typora 主题

#### 主题架构

**亮色主题：** `typora/themes/vue-laomst/`
**暗色主题：** `typora/themes/vue-laomst-dark/`

**入口文件：** `vue-laomst.css` - 导入所有 CSS 模块并定义核心 CSS 自定义属性

**模块化组件：**
| 模块 | 功能 |
|------|------|
| `font-family/` | Monaco 字体（base64 编码） |
| `headline/` | 标题样式（CSS 计数器实现层级编号） |
| `blockquote/` | 引用块样式（含标题变体） |
| `code-block/` | 代码块语法高亮（gitlib 主题） |
| `code-line/` | 行内代码样式 |
| `ul-ol/` | 列表样式 |
| `table/` | 表格格式化 |
| `a/` | 链接样式 |
| `foot-note/` | 脚注格式化 |
| `outline/` | 文档大纲样式 |
| `heigh-light/` | 文本高亮 |

#### 安装主题

1. 复制主题文件夹到 Typora 主题目录：
   - macOS: `~/Library/Application Support/abnerworks.Typora/themes/`
   - Windows: `%APPDATA%\Typora\themes\`
2. 重启 Typora 并选择主题

#### 切换样式变体

编辑模块的索引文件（如 `code-block/code-block.css`），修改 `@import` 语句指向不同的变体文件。

**无需构建过程** - CSS 文件直接被 Typora 使用。

### 快捷键

Windows 快捷键配置在 `typora/key_mappings/key-mapping-windows.json`。

---

## Git 提交规范

Claude 提交时，**必须根据当前使用的模型选择对应的作者签名**：

| 启动方式 | 模型 | 提交作者 |
|----------|------|----------|
| `claude-glm` | glm-4.7 | `laomst-cc_glm4.7` |
| `claude-minimax` | MiniMax-M2.1 | `laomst-cc_minimax` |

手动提交使用本地配置：`laomst <laomst@163.com>`

自动检测模型并提交的命令：
```bash
case "$ANTHROPIC_MODEL" in
  glm-4.7*)   AUTHOR="laomst-cc_glm4.7<laomst@163.com>" ;;
  MiniMax*)   AUTHOR="laomst-cc_minimax<laomst@163.com>" ;;
  *)          AUTHOR="laomst-cc<laomst@163.com>" ;;
esac
git commit -m "提交信息" --author="$AUTHOR"
```
