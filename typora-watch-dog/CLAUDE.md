# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Typora Watch Dog 是一个 Python 文件监控服务，自动管理 Typora Markdown 工作区：
- 监听文件变化（创建、移动、删除、修改），自动添加/更新 YAML front matter（`serial`、`typora-watch-dog-root-url`、`typora-watch-dog-copy-images-to`）
- 维护 `.index/path_index.json` 索引文件，记录 serial 到文件路径的映射
- 管理图片资源的集中存储（`.assets/{serial首字母}/{serial}/`）

## 运行与开发

```bash
# 环境准备
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# 启动监控（前台）
python src/watch_workspace.py -w <workspace_path>

# 守护进程
python src/watch_workspace.py -w <workspace_path> -d
python src/watch_workspace.py --stop
python src/watch_workspace.py --status

# 通过 shell 包装脚本启动（自动激活 venv）
./watch.sh
```

环境变量 `TYPORA_WORKSPACE` 可替代 `-w` 参数。

## 架构

三个核心模块，单向依赖关系：`watch_workspace.py` → `index_typora_markdowns.py` → `move_assets_to_root_url.py`

- **`src/watch_workspace.py`**：主入口。使用 watchdog 库监听文件系统事件，通过 `DebounceManager`（10秒窗口）去重，`MarkdownEventHandler` 分发处理。支持 PID 守护进程管理、日志按日轮转（30天保留）。
- **`src/index_typora_markdowns.py`**：核心逻辑。生成 8 字符 serial（首位字母+7位字母数字），管理 front matter 的创建与更新，维护索引文件。公开 API：`index_or_update_file(workspace, file)` 和 `remove_from_index(workspace, file)`。
- **`src/move_assets_to_root_url.py`**：资源迁移工具。将图片从 `{file}/.assets/{filename}/` 迁移到 serial 目录结构，同时更新 markdown 中的图片链接。
- **`src/util/`**：`logger.py` 提供日志策略（console/file/disabled），`io_util.py` 提供递归文件查找。

## 关键设计约定

- **serial 生成规则**：8字符，首位必须是字母，其余为字母数字混合
- **front matter 处理**：幂等操作——已有 serial 则保留，仅在路径变化时更新 root-url 和 copy-images-to
- **文件过滤**：跳过 Untitled 文件、冲突文件、备份文件（`*.md~`）
- **路径计算**：根据文件在工作区中的深度，计算 `../` 相对路径作为 root-url
- **平台支持**：Linux（systemd）、macOS（launchd）、Windows（NSSM），服务安装脚本在 `service-install/`
