# 文件监控服务使用指南

> **注意：** 以下命令均应在 `typora/` 目录下执行。

## 概述

`watch_workspace.py` 是一个文件系统监控服务，可以自动监控 Typora 工作空间中的 Markdown 文件变化，并自动更新索引。

## 功能特性

| 事件类型 | 处理方式 |
|---------|---------|
| 新建 .md 文件 | 自动添加 front matter（article-id、typora-root-url、typora-copy-images-to）并更新索引 |
| 移动 .md 文件 | 自动更新 typora-root-url 和索引中的路径 |
| 删除 .md 文件 | 自动从索引中移除 |
| 修改 .md 文件 | 检查并更新 front matter（带防抖，避免频繁触发） |

## 安装

### 1. 安装依赖

```bash
pip install -r scripts/requirements.txt
# 或
pip install watchdog
```

### 2. 配置工作空间

```bash
# 方式 1: 环境变量
export TYPORA_WORKSPACE=/path/to/your/workspace

# 方式 2: 命令行参数
python scripts/watch_workspace.py -w /path/to/workspace
```

## 使用方式

### 方式 1: 手动运行（前台）

```bash
# 使用环境变量中的工作空间
python scripts/watch_workspace.py

# 指定工作空间路径
python scripts/watch_workspace.py -w /path/to/workspace

# 调整防抖延迟（默认 1 秒）
python scripts/watch_workspace.py --debounce-delay 2.0

# 手动验证并修复索引（不启动监控）
python scripts/watch_workspace.py --verify-index

# 清理旧日志（默认保留 30 天）
python scripts/watch_workspace.py --clean-logs

# 清理旧日志（指定保留天数）
python scripts/watch_workspace.py --clean-logs --log-retention 7
```

### 方式 2: 后台运行

```bash
# Unix/Linux/macOS
python scripts/watch_workspace.py --daemon

# 停止后台运行
python scripts/watch_workspace.py --stop

# 查看运行状态
python scripts/watch_workspace.py --status
```

### 方式 3: 系统服务（开机自启）

#### Linux (systemd)

```bash
# 安装服务
sudo ./install-service.sh install

# 管理服务
sudo ./install-service.sh {start|stop|restart|status|logs}

# 卸载服务
sudo ./install-service.sh uninstall
```

#### macOS (launchd)

```bash
# 安装服务（注意：不要使用 sudo，LaunchAgent 是用户级服务）
./install-service.sh install

# 或指定工作空间路径
TYPORA_WORKSPACE=/path/to/workspace ./install-service.sh install

# 管理服务
./install-service.sh {start|stop|restart|status|logs}

# 卸载服务
./install-service.sh uninstall
```

> **重要提示：** macOS 使用 LaunchAgent（用户级服务），**不应使用 sudo** 运行安装脚本。使用 sudo 会导致文件权限问题。

#### Windows (NSSM)

参考 [`windows-nssm.md`](windows-nssm.md) 文档。

## 配置说明

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `TYPORA_WORKSPACE` | Typora 工作空间根目录的绝对路径 | 是 |

### 命令行参数

```
-w, --workspace       工作空间路径
-d, --daemon          后台运行模式（Unix-like）
--stop                停止后台运行的服务
--status              查看服务运行状态
--no-log-file         不写入日志文件
--debounce-delay      防抖延迟时间（秒），默认 1.0
--verify-index        验证并修复索引（不启动监控）
--log-retention DAYS  日志保留天数（默认 30 天）
--clean-logs          清理旧日志后退出（不启动监控）
```

## 工作原理

```
┌─────────────────────────────────────────────────────┐
│              watch_workspace.py                      │
│  ┌─────────────────────────────────────────────┐   │
│  │         Watchdog Observer                    │   │
│  │  监听文件系统事件（创建、移动、删除、修改）   │   │
│  └─────────────────────────────────────────────┘   │
│                      ↓                              │
│  ┌─────────────────────────────────────────────┐   │
│  │         Debounce (防抖)                      │   │
│  │  • 同一文件 1 秒内只触发一次                 │   │
│  │  • 避免编辑时频繁触发                        │   │
│  └─────────────────────────────────────────────┘   │
│                      ↓                              │
│  ┌─────────────────────────────────────────────┐   │
│  │    index_typora_markdowns.py (调用)          │   │
│  │  • 添加/更新 front matter                    │   │
│  │  • 更新 .index.json 索引文件                 │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## 索引验证

服务启动时会自动验证索引完整性，并修复错误的路径：

1. **检查文件是否存在** - 遍历索引中的每个 article-id
2. **搜索移动的文件** - 如果文件不存在，在工作空间中搜索（通过 article-id）
3. **更新索引** - 修复找到的文件路径，移除不存在的索引
4. **显示结果** - 输出验证、修复、移除的文件数量

### 手动触发验证

```bash
# 仅验证索引，不启动监控
python scripts/watch_workspace.py --verify-index

# 输出示例：
# 工作空间: /path/to/workspace
# 开始验证并修复索引...
#
# 验证完成:
#   已验证: 473 个文件
#   已修复: 2 个路径
#   已移除: 4 个无效索引
```

### 验证逻辑

| 场景 | 处理方式 |
|------|---------|
| 文件存在且路径正确 | 无操作 |
| 文件存在但路径错误 | 更新索引中的路径 |
| 文件不存在但在工作空间找到 | 更新索引并修复 front matter |
| 文件不存在且找不到 | 从索引中移除 |

## 日志

### 日志位置

| 类型 | 路径 | 说明 |
|------|------|------|
| 日志目录 | `~/.typora-ext-logs/` | 所有日志文件存储目录 |
| 当日日志 | `~/.typora-ext-logs/typora-watch-YYYY-MM-DD.log` | 按日期命名的日志文件 |
| PID 文件 | `~/.typora-ext-watch.pid` | 后台进程 PID 文件 |

### 日志管理

**按日期存储：**
- 每天自动创建新的日志文件
- 文件名格式：`typora-watch-2026-02-04.log`
- 默认保留 30 天的日志

**自动清理：**
- 服务启动时自动清理超过保留天数的旧日志
- 可通过 `--log-retention` 参数调整保留天数

**手动清理：**
```bash
# 清理旧日志（使用默认保留天数）
python scripts/watch_workspace.py --clean-logs

# 清理超过 7 天的日志
python scripts/watch_workspace.py --clean-logs --log-retention 7
```

### 查看日志

```bash
# 查看日志目录
ls -la ~/.typora-ext-logs/

# 实时查看当日日志
LOG_FILE=$(ls -t ~/.typora-ext-logs/typora-watch-*.log 2>/dev/null | head -1)
tail -f "$LOG_FILE"

# 查看指定日期的日志
tail -100 ~/.typora-ext-logs/typora-watch-2026-02-04.log

# 搜索最近日志中的错误
grep ERROR ~/.typora-ext-logs/typora-watch-*.log | tail -20
```

## 故障排查

### 服务无法启动

1. 检查工作空间路径是否正确
2. 检查 Python 和 watchdog 是否安装
3. 查看日志文件获取详细错误信息

### 文件未被索引

1. 检查文件是否在工作空间内
2. 检查文件扩展名是否为 `.md`
3. 查看日志确认事件是否被捕获

### 防抖延迟设置

如果发现编辑时触发频繁，增加防抖延迟：

```bash
python scripts/watch_workspace.py --debounce-delay 2.0
```

如果希望更快响应，减少延迟：

```bash
python scripts/watch_workspace.py --debounce-delay 0.5
```
