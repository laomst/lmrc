# Zsh Shell 配置

个人 Zsh Shell 环境配置文件。

## 平台支持

| 平台 | 支持状态 | 说明 |
|------|----------|------|
| **Linux** | ✅ 完全支持 | 需先安装 zsh，在 `~/.zshrc` 中添加 source 命令 |
| **macOS** | ✅ 完全支持 | 默认 shell（Catalina 及以后），在 `~/.zshrc` 中添加 |
| **Windows (WSL)** | ✅ 完全支持 | 需先安装 zsh，在 `~/.zshrc` 中添加 source 命令 |
| **Windows (原生)** | ❌ 不支持 | 请使用 WSL 或等待 PowerShell 配置 |

> **重要提示：** 本配置不支持 Windows 原生环境（PowerShell/CMD）。Windows 用户请：
> 1. 使用 WSL (Windows Subsystem for Linux) 安装 Linux 发行版
> 2. 或等待后续发布的 PowerShell 配置

## 安装方式

### Linux / WSL

首先确保已安装 zsh：

```bash
# Ubuntu/Debian
sudo apt install zsh

# CentOS/RHEL
sudo yum install zsh

# 设置为默认 shell（可选）
chsh -s $(which zsh)
```

在 `~/.zshrc` 中添加：

```zsh
source ~/lmrc/zsh/index.zsh
```

### macOS

macOS Catalina (10.15) 及以后版本默认使用 zsh。

在 `~/.zshrc` 中添加：

```zsh
source ~/lmrc/zsh/index.zsh
```

## 配置文件说明

| 文件 | 说明 |
|------|------|
| `index.zsh` | 入口文件，按顺序加载其他配置 |
| `exports.zsh` | 本地环境变量（不提交到仓库，需自行创建） |
| `path.zsh` | PATH 和 SDK 路径配置 |
| `function.zsh` | 自定义工具函数 |
| `alias.zsh` | 命令别名 |
| `completion.zsh` | Shell 自动补全 |
| `prompt.zsh` | 提示符定制（含 git 状态） |
| `claude.zsh` | Claude Code 模型切换函数 |

## 加载顺序

1. `exports.zsh` - 本地环境变量（如果存在）
2. `path.zsh` - PATH 和 SDK 变量
3. `function.zsh` - 自定义函数
4. `alias.zsh` - 命令别名
5. `completion.zsh` - 自动补全
6. `prompt.zsh` - 提示符定制
7. `claude.zsh` - 模型切换函数
8. 其他 `.zsh` 文件（自动发现并加载）

## 本地环境变量

创建 `exports.zsh` 来存放个人配置（不提交到 Git）：

```zsh
# API Keys
export OPENAI_API_KEY="sk-xxx"
export ANTHROPIC_API_KEY="sk-ant-xxx"

# 本地路径
export MY_PROJECTS="$HOME/Projects"
```

## Claude Code 模型切换

`claude.zsh` 提供了便捷的模型切换函数：

```zsh
# 使用 GLM (智谱 AI) 模型
claude-glm "帮我写一个函数"

# 使用 MiniMax 模型
claude-minimax "帮我分析代码"
```

## SDK 配置

在 `path.zsh` 中配置常用 SDK 路径：

- `JAVA_HOME`、`JAVA8_HOME`、`JAVA21_HOME` - Java 版本
- `MAVEN_HOME` - Maven 位置
- `PYTHON_HOME` - Python 框架路径

## Windows 用户

如果你使用的是 Windows 原生环境（非 WSL），本配置**无法使用**。推荐方案：

1. **启用 WSL**（推荐）：
   ```powershell
   wsl --install
   ```
   安装 Ubuntu 或其他 Linux 发行版后，在 WSL 中安装 zsh：
   ```bash
   sudo apt install zsh
   ```

2. **等待 PowerShell 配置**：
   后续会发布专门的 PowerShell 配置，敬请期待。
