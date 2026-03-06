# Typora Watch Dog

Typora 工作空间文件监控服务。自动监听 Markdown 文件的创建、移动、删除等变化，维护 YAML front matter 和文件索引。

## 功能

- **自动添加 front matter** — 新建 `.md` 文件时自动注入 `serial`、`typora-watch-dog-root-url`、`typora-watch-dog-copy-images-to` 字段
- **文件移动追踪** — 移动文件后自动更新 `typora-watch-dog-root-url` 和索引路径
- **索引维护** — 在 `.index/path_index.json` 中维护 serial 到文件路径的映射
- **图片资源集中管理** — 将图片存储到基于 serial 的统一目录结构（`.assets/{serial首字母}/{serial}/`）
- **事件防抖** — 同一文件同一事件类型在 10 秒内仅触发一次，避免编辑器保存时的重复处理
- **索引验证与修复** — 启动时自动校验索引完整性，支持手动触发验证

## 快速开始

### 安装

```bash
git clone <repository-url>
cd typora-watch-dog
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

依赖项仅 `watchdog>=4.0.0`。如果跳过手动安装，服务启动时也会自动检测并安装。

### 运行

```bash
# 前台运行（指定工作空间路径）
python src/watch_workspace.py -w /path/to/workspace

# 或通过环境变量指定
export TYPORA_WORKSPACE=/path/to/workspace
python src/watch_workspace.py

# 使用 shell 包装脚本（自动激活 venv）
./watch.sh
```

## 使用方式

### 手动运行

```bash
# 前台运行
python src/watch_workspace.py -w /path/to/workspace

# 调整防抖延迟（默认 1 秒）
python src/watch_workspace.py --debounce-delay 2.0

# 仅验证并修复索引（不启动监控）
python src/watch_workspace.py --verify-index

# 清理旧日志
python src/watch_workspace.py --clean-logs
python src/watch_workspace.py --clean-logs --log-retention 7
```

### 后台守护进程（Unix/Linux/macOS）

```bash
python src/watch_workspace.py -d          # 启动
python src/watch_workspace.py --status    # 查看状态
python src/watch_workspace.py --stop      # 停止
```

### 系统服务（开机自启）

#### Linux（systemd）

```bash
sudo ./service-install/install-service.sh install
sudo ./service-install/install-service.sh {start|stop|restart|status|logs}
sudo ./service-install/install-service.sh uninstall
```

#### macOS（launchd）

> macOS 使用 LaunchAgent（用户级服务），**不要使用 sudo**。

```bash
./service-install/install-service.sh install
./service-install/install-service.sh {start|stop|restart|status|logs}
./service-install/install-service.sh uninstall

# 安装时指定工作空间路径
TYPORA_WORKSPACE=/path/to/workspace ./service-install/install-service.sh install
```

#### Windows（NSSM）

参见 [service-install/windows-nssm.md](service-install/windows-nssm.md)。

## 命令行参数

| 参数 | 说明 |
|------|------|
| `-w, --workspace` | 工作空间路径（也可通过 `TYPORA_WORKSPACE` 环境变量设置） |
| `-d, --daemon` | 后台守护进程模式（仅 Unix-like 系统） |
| `--stop` | 停止守护进程 |
| `--status` | 查看运行状态 |
| `--no-log-file` | 不写入日志文件 |
| `--debounce-delay` | 防抖延迟时间（秒），默认 1.0 |
| `--verify-index` | 验证并修复索引后退出（不启动监控） |
| `--log-retention DAYS` | 日志保留天数，默认 30 |
| `--clean-logs` | 清理过期日志后退出 |

## 工作原理

### 事件处理流程

```
文件系统事件（watchdog 捕获）
        ↓
   事件防抖（10 秒去重）
        ↓
   事件分发处理
   ├── 新建 → 添加 front matter + 更新索引
   ├── 移动 → 移除旧索引 + 更新 front matter + 更新索引
   ├── 删除 → 从索引中移除
   └── 修改 → 仅记录日志
```

### Front Matter 结构

每个 Markdown 文件被添加如下 YAML front matter：

```yaml
---
serial: a1b2c3d4
typora-watch-dog-root-url: ../../
typora-watch-dog-copy-images-to: ../../.assets/a/a1b2c3d4
---
```

| 字段 | 说明 |
|------|------|
| `serial` | 8 字符唯一标识（首位字母，其余字母数字混合） |
| `typora-watch-dog-root-url` | 文件到工作空间根目录的相对路径（`../` 形式） |
| `typora-watch-dog-copy-images-to` | 图片存储目录的相对路径 |

### Front Matter 处理策略

- **无 front matter** → 生成新 serial，添加完整 front matter
- **有 front matter 但无 serial** → 生成 serial，重新计算路径，保留其他已有字段
- **有 front matter 且有 serial** → 保留 serial 和其他字段，仅在路径变化时更新

### 索引文件

索引存储在工作空间根目录的 `.index/path_index.json`：

```json
{
  "a1b2c3d4": "/notes/example.md",
  "b2c3d4e5": "/blog/post.md"
}
```

### 文件过滤规则

以下文件会被自动跳过：

- 文件名以 `Untitled` 开头（Typora 未命名的新建文件）
- 文件名包含「冲突文件」
- 备份文件（`*.md~`）

### 索引验证

启动时自动验证索引完整性，也可手动触发：

```bash
python src/watch_workspace.py --verify-index
```

验证逻辑：

| 场景 | 处理方式 |
|------|---------|
| 文件存在且路径正确 | 无操作 |
| 文件存在但路径错误 | 更新索引中的路径 |
| 文件不存在但在工作空间找到 | 更新索引并修复 front matter |
| 文件不存在且找不到 | 从索引中移除 |

## 图片迁移工具

`move_assets_to_root_url.py` 用于将旧格式的图片目录迁移到 serial 目录结构。

```bash
# 模拟运行（查看将要执行的操作）
python src/move_assets_to_root_url.py -w /path/to/workspace --dry-run

# 实际执行
python src/move_assets_to_root_url.py -w /path/to/workspace
```

迁移过程：
1. 将图片从 `.assets/{文件名}/` 移动到 `.assets/{serial首字母}/{serial}/`
2. 更新 Markdown 文件中的图片链接
3. 清理空的旧目录

## 索引模块命令行

`index_typora_markdowns.py` 可独立使用，手动为文件添加 front matter：

```bash
# 处理单个文件
python src/index_typora_markdowns.py -w /workspace file.md

# 处理目录（递归）
python src/index_typora_markdowns.py -w /workspace directory/

# 处理多个路径
python src/index_typora_markdowns.py -w /workspace file1.md file2.md dir/
```

## 项目结构

```
typora-watch-dog/
├── src/
│   ├── watch_workspace.py           # 主服务：文件监控 + 事件分发
│   ├── index_typora_markdowns.py    # 核心模块：front matter 管理 + 索引维护
│   ├── move_assets_to_root_url.py   # 工具：图片资源迁移
│   └── util/
│       ├── logger.py                # 日志工具
│       └── io_util.py               # 文件 I/O 工具
├── service-install/
│   ├── install-service.sh           # 系统服务安装脚本（systemd / launchd）
│   ├── README.md                    # 服务安装详细指南
│   └── windows-nssm.md             # Windows NSSM 安装指南
├── watch.sh                         # 启动包装脚本（自动激活 venv）
└── requirements.txt                 # Python 依赖（watchdog>=4.0.0）
```

模块依赖关系：`watch_workspace.py` → `index_typora_markdowns.py` → `move_assets_to_root_url.py`

## 日志

| 项目 | 说明 |
|------|------|
| 日志目录 | `~/.typora-ext-logs/` |
| 当前日志 | `typora-watch-dog-watch.log` |
| 历史日志 | `typora-watch-dog-watch.YYYY-MM-DD.log`（每日午夜自动轮转） |
| PID 文件 | `~/.typora-ext-watch.pid` |
| 默认保留 | 30 天 |

```bash
# 实时查看日志
tail -f ~/.typora-ext-logs/typora-watch-dog-watch.log

# 搜索错误
grep ERROR ~/.typora-ext-logs/typora-watch-dog-watch*.log | tail -20
```

## 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `TYPORA_WORKSPACE` | 工作空间根目录的绝对路径 | 是（或使用 `-w` 参数） |
| `TYPORA_WATCH_SERVICE` | 设为 `true` 标识以系统服务模式运行 | 否（服务安装脚本自动设置） |
| `PYTHON_BIN` | Python 可执行文件路径（默认 `python3`） | 否 |

## 许可证

MIT
