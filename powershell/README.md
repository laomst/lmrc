# PowerShell 模块化配置框架

模块化的 PowerShell 环境配置框架，与 `zsh/` 框架对等设计。

## 快速开始

1. 复制配置模板：

```powershell
Copy-Item includes_example.ini includes.ini
```

2. 在 PowerShell Profile 中添加加载入口：

```powershell
# 查看 Profile 路径
$PROFILE

# 编辑 Profile 添加以下内容
. "C:\path\to\lmrc\powershell\index.ps1"
```

3. 重新打开 PowerShell 即可生效。

## 架构

六阶段有序加载流程，每个阶段前后提供 hook 点：

```
pre_export  → exports.ps1   → post_export
pre_path    → path.ps1      → post_path
pre_function→ function.ps1  → post_function
pre_alias   → alias.ps1     → post_alias
pre_completion→ completion.ps1→ post_completion
pre_prompt  → prompt.ps1    → post_prompt
pre_others  → 其余 *.ps1   → post_others → post_all
```

通过 `includes.ini` 在各 hook 点注入机器相关的扩展脚本。

## 文件说明

| 文件 | 用途 |
|------|------|
| `index.ps1` | 入口文件，定义六阶段加载流程 |
| `include.ps1` | 预加载器，加载 `includes/` 目录下的模块 |
| `includes/01-common.ps1` | 公共工具函数（`Check-EnvExists` 等） |
| `includes/02-loader.ps1` | INI 解析器，提供 `Load-LmrcScript` / `Load-LmrcSection` |
| `exports.ps1` | 环境变量配置（SDK 路径等） |
| `path.ps1` | PATH 环境变量管理 |
| `function.ps1` | 函数加载器（自动加载 `functions/` 目录） |
| `functions/01-fs.ps1` | 文件系统工具函数（mkcd、back、which） |
| `alias.ps1` | 命令别名和 Git 快捷方式 |
| `completion.ps1` | 自动补全配置（PSReadLine + ArgumentCompleter） |
| `prompt.ps1` | 提示符定制（时间、用户、Git 分支） |
| `includes.ini` | 机器相关扩展配置（不提交） |
| `includes_example.ini` | 配置模板 |

## 自定义扩展

编辑 `includes.ini`，在对应 section 下添加脚本绝对路径：

```ini
[post_export]
C:\Users\me\scripts\my-exports.ps1

[post_alias]
C:\Users\me\scripts\my-aliases.ps1
```

添加自定义函数：在 `functions/` 目录下创建编号文件（如 `02-network.ps1`），会被自动加载。
