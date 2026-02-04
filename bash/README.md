# Bash Shell 配置

个人 Bash Shell 环境配置文件。

## 平台支持

| 平台 | 支持状态 | 说明 |
|------|----------|------|
| **Linux** | ✅ 完全支持 | 在 `~/.bashrc` 中添加 source 命令 |
| **macOS** | ✅ 完全支持 | 在 `~/.bash_profile` 中添加 source 命令 |
| **Windows (WSL)** | ✅ 完全支持 | 在 `~/.bashrc` 中添加 source 命令 |
| **Windows (原生)** | ❌ 不支持 | 请使用 WSL 或等待 PowerShell 配置 |

> **重要提示：** 本配置不支持 Windows 原生环境（PowerShell/CMD）。Windows 用户请：
> 1. 使用 WSL (Windows Subsystem for Linux) 安装 Linux 发行版
> 2. 或等待后续发布的 PowerShell 配置

## 安装方式

### Linux / WSL

在 `~/.bashrc` 中添加：

```bash
source ~/lmrc/bash/index.sh
```

### macOS

在 `~/.bash_profile` 中添加：

```bash
source ~/lmrc/bash/index.sh
```

## 配置文件说明

| 文件 | 说明 |
|------|------|
| `index.sh` | 入口文件，按顺序加载其他配置 |
| `exports.sh` | 本地环境变量（不提交到仓库，需自行创建） |
| `path.sh` | PATH 和 SDK 路径配置 |
| `function.sh` | 自定义工具函数 |
| `alias.sh` | 命令别名 |
| `completion.sh` | Shell 自动补全 |
| `prompt.sh` | 提示符定制 |

## 加载顺序

1. `exports.sh` - 本地环境变量（如果存在）
2. `path.sh` - PATH 和 SDK 变量
3. `function.sh` - 自定义函数
4. `alias.sh` - 命令别名
5. `completion.sh` - 自动补全
6. `prompt.sh` - 提示符定制
7. 其他 `.sh` 文件（自动发现并加载）

## 本地环境变量

创建 `exports.sh` 来存放个人配置（不提交到 Git）：

```bash
# API Keys
export OPENAI_API_KEY="sk-xxx"
export ANTHROPIC_API_KEY="sk-ant-xxx"

# 本地路径
export MY_PROJECTS="$HOME/Projects"
```

## Windows 用户

如果你使用的是 Windows 原生环境（非 WSL），本配置**无法使用**。推荐方案：

1. **启用 WSL**（推荐）：
   ```powershell
   wsl --install
   ```
   安装 Ubuntu 或其他 Linux 发行版后，在 WSL 环境中使用本配置。

2. **等待 PowerShell 配置**：
   后续会发布专门的 PowerShell 配置，敬请期待。
