# lmrc/zsh

模块化的 zsh 环境配置框架。将 shell 配置拆分为独立模块，按固定顺序加载，并通过 INI 配置文件提供灵活的扩展点。

## 快速开始

将项目克隆到任意目录，然后在 `~/.zshrc` 中添加一行：

```bash
source /path/to/lmrc/zsh/index.zsh
```

将 `/path/to/lmrc` 替换为项目实际所在的路径。

如需自定义扩展脚本，复制示例配置：

```bash
cp includes_example.ini includes.ini
```

然后在 `includes.ini` 对应的 section 中添加外部脚本路径即可。

## 加载流程

`index.zsh` 按以下顺序加载配置模块，每个模块前后均有 hook 点可通过 `includes.ini` 注入外部脚本：

```
include.zsh          ← 预加载（INI 解析器、工具函数）
  │
  ├─ [pre_export]
  ├─ exports.zsh     ← 环境变量（JAVA_HOME、MAVEN_HOME 等）
  ├─ [post_export]
  │
  ├─ [pre_path]
  ├─ path.zsh        ← PATH 环境变量
  ├─ [post_path]
  │
  ├─ [pre_function]
  ├─ function.zsh    ← 自动加载 functions/ 目录下所有函数
  ├─ [post_function]
  │
  ├─ [pre_alias]
  ├─ alias.zsh       ← 命令别名
  ├─ [post_alias]
  │
  ├─ [pre_completion]
  ├─ completion.zsh  ← 自动补全配置
  ├─ [post_completion]
  │
  ├─ [pre_prompt]
  ├─ prompt.zsh      ← 提示符（含 git 分支信息）
  ├─ [post_prompt]
  │
  ├─ [pre_others]
  ├─ *.zsh           ← 根目录下其余 .zsh 文件
  ├─ [post_others]
  │
  └─ [post_all]      ← 所有加载完成后的最终 hook
```

加载完成后自动清理所有临时变量和工具函数（`load_script`、`load_section`、`_parse_ini` 等）。

## includes.ini 扩展机制

`includes.ini` 用于在各加载阶段注入机器相关的外部脚本，不同机器可以有不同的配置。

格式规则：
- `[section_name]` 标记加载阶段
- 每行一个**绝对路径**（以 `/` 或 `~` 开头），相对路径会被忽略
- 支持 `~` 和 `$HOME` 等环境变量展开
- `#` 开头为注释，空行被忽略
- 不存在的文件静默跳过

示例：

```ini
[pre_export]
~/my-configs/env-override.zsh

[post_all]
/opt/company/shell-tools/init.zsh
```

> `includes.ini` 是机器相关配置，`includes_example.ini` 是模板。

## 目录结构

```
index.zsh               # 入口文件
include.zsh             # 预加载 includes/ 目录
includes/
  01-common.zsh         # 公共工具函数（check-env-exists 等）
  02-loader.zsh         # INI 解析器，提供 load_script / load_section
  03-prompt-select.zsh  # 交互式选择菜单（prompt-select）
includes.ini            # 扩展脚本配置（机器相关）
includes_example.ini    # 配置模板
exports.zsh             # 环境变量
path.zsh                # PATH 配置
function.zsh            # 函数加载器（自动加载 functions/ 目录）
functions/
  01-fs.zsh             # 文件系统操作
  02-network.zsh        # 网络工具
  03-git.zsh            # Git 快捷操作
  04-search.zsh         # 搜索工具
  05-process.zsh        # 进程管理
  06-dev.zsh            # 开发辅助工具
  07-system.zsh         # 系统信息与工具
  08-archive.zsh        # 压缩/解压
alias.zsh               # 命令别名
completion.zsh          # 自动补全
prompt.zsh              # 提示符配置
```

## 内置工具函数

### 文件系统

| 函数 | 说明 | 用法 |
|------|------|------|
| `mkcd` | 创建目录并进入 | `mkcd new-project` |
| `back` | 快速回退 N 层目录 | `back 3` |
| `duf` | 查看文件/目录大小（降序） | `duf *` |
| `largest` | 当前目录最大的 N 项 | `largest 20` |

### 网络

| 函数 | 说明 | 用法 |
|------|------|------|
| `myip` | 获取本机局域网 IP | `myip` |
| `publicip` | 获取公网 IP | `publicip` |
| `testport` | 测试端口连通性 | `testport 192.168.1.1 22` |

### Git

| 函数 | 说明 | 用法 |
|------|------|------|
| `gitlog` | 美化 git 日志（单行图形） | `gitlog -20` |
| `gitgraph` | 分支图 | `gitgraph` |
| `gbn` | 创建并切换新分支 | `gbn feature/login` |

### 搜索

| 函数 | 说明 | 用法 |
|------|------|------|
| `fif` | 递归搜索文件内容 | `fif "TODO"` |
| `fn` | 按文件名搜索 | `fn "*.config"` |

### 进程

| 函数 | 说明 | 用法 |
|------|------|------|
| `psgrep` | 按名称查找进程 | `psgrep nginx` |
| `pskill` | 按名称杀死进程 | `pskill nginx` |

### 开发工具

| 函数 | 说明 | 用法 |
|------|------|------|
| `server` | 启动 HTTP 服务器（Python） | `server 3000` |
| `jsonfmt` | 格式化 JSON 文件 | `jsonfmt data.json` |

### 系统

| 函数 | 说明 | 用法 |
|------|------|------|
| `diskusage` | 磁盘使用情况 | `diskusage` |
| `memusage` | 内存使用情况 | `memusage` |
| `pathls` | 列出 PATH（`-i` 分块显示） | `pathls -i` |
| `colors256` | 显示 256 色色板 | `colors256` |
| `histgrep` | 搜索命令历史 | `histgrep docker` |
| `stopwatch` | 秒表（Ctrl+C 停止） | `stopwatch` |

### 压缩/解压

| 函数 | 说明 | 用法 |
|------|------|------|
| `extract` | 智能解压（支持 tar.gz/zip/rar/7z 等） | `extract archive.tar.gz` |
| `targz` | 创建 tar.gz 压缩包 | `targz my-folder` |

## 内置别名

```bash
# 文件列表
ll    → ls -alF
la    → ls -A
l     → ls -CF
lsa   → ls -a

# 目录跳转
..    → cd ..
...   → cd ../..
~     → cd ~

# Python
python → python3
pip    → pip3

# Git
gs    → git status
ga    → git add
gc    → git commit
gp    → git push
```

## 自定义扩展

### 添加新的工具函数

在 `functions/` 目录下创建新文件，按编号命名：

```bash
# functions/09-docker.zsh
dps() { docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" }
```

重新打开终端即可自动加载。

### 添加机器相关的配置

编辑 `includes.ini`，在合适的 section 中添加外部脚本路径：

```ini
[post_all]
~/work/company-env.zsh
```
