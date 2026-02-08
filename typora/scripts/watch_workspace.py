#!/usr/bin/env python3
"""
Typora 工作空间文件监控服务

监控工作空间中的 Markdown 文件变化，自动触发索引更新。

监控事件：
- 新建 .md 文件 → 自动添加 front matter 和索引
- 移动 .md 文件 → 自动更新 typora-root-url 和索引
- 修改 .md 文件 → 仅记录日志，不做操作
- 删除 .md 文件 → 从索引中移除（不删除 assets 目录）

防抖机制：
- 同一文件的同一事件在 10 秒内仅触发一次
- 防止短时间内重复处理（如编辑器保存时的多次事件）
- 支持的事件类型：created、moved、deleted、modified

依赖管理：
- 启动时自动检查并安装必要的依赖（watchdog）
- 如果自动安装失败，会提示手动安装命令

日志管理：
- 使用 TimedRotatingFileHandler 实现每天午夜自动轮转日志文件
- 日志文件格式：typora-watch.log（当前）、typora-watch.YYYY-MM-DD.log（历史）
- 自动清理超过保留天数的旧日志文件
- 默认保留 30 天的日志（可通过 --log-retention 参数调整）

使用方式：
    # 手动运行（前台）
    python watch_workspace.py

    # 指定工作空间路径
    python watch_workspace.py -w /path/to/workspace

    # 后台运行
    python watch_workspace.py --daemon

    # 停止后台运行
    python watch_workspace.py --stop

    # 清理旧日志
    python watch_workspace.py --clean-logs

系统服务安装：
    # Linux (systemd)
    sudo ../service-install/install-service.sh install

    # macOS (launchd)
    sudo ../service-install/install-service.sh install

    # Windows (使用 NSSM)
    # 参考 ../service-install/windows-nssm.md
"""

import argparse
import atexit
import logging
import os
import sys
import time
from collections import defaultdict
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Dict, Optional, Tuple

# 环境变量名称
TYPORA_WORKSPACE_ENV = 'TYPORA_WORKSPACE'

# PID 文件路径（用于后台运行管理）
PID_FILE = os.path.expanduser('~/.typora-ext-watch.pid')

# 日志目录
LOG_DIR = os.path.expanduser('~/.typora-ext-logs')
# 日志文件保留天数（默认 30 天）
DEFAULT_LOG_RETENTION_DAYS = 30

# 导入索引模块
try:
    from index_typora_markdowns import (
        index_or_update_file,
        remove_from_index,
        TYPORA_WORKSPACE_ENV,
    )
except ImportError:
    # 如果导入失败，尝试从同一目录导入
    sys.path.insert(0, os.path.dirname(__file__))
    from index_typora_markdowns import (
        index_or_update_file,
        remove_from_index,
        TYPORA_WORKSPACE_ENV,
    )

# 导入 watchdog（如果不可用会在 main 时报错）
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    Observer = None
    FileSystemEventHandler = None


def check_and_install_dependencies() -> None:
    """
    检查并安装必要的依赖

    检查 watchdog 是否安装，如果没有则自动安装
    """
    import subprocess

    dependencies = {
        'watchdog': 'watchdog',
    }

    for module_name, package_name in dependencies.items():
        try:
            __import__(module_name)
        except ImportError:
            get_logger().warning(f'未安装 {module_name} 模块，正在自动安装...')
            try:
                subprocess.check_call(
                    [sys.executable, '-m', 'pip', 'install', '--break-system-packages', package_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                get_logger().info(f'✓ {module_name} 安装成功')
                # 重新导入验证
                __import__(module_name)
            except subprocess.CalledProcessError:
                get_logger().error(f'✗ {module_name} 安装失败')
                get_logger().error(f'请手动运行: pip install {package_name}')
                sys.exit(1)
            except Exception as e:
                get_logger().error(f'✗ {module_name} 安装失败: {e}')
                sys.exit(1)


def setup_logger(log_to_file: bool = True, log_retention_days: int = DEFAULT_LOG_RETENTION_DAYS) -> logging.Logger:
    """
    设置日志系统（幂等性：多次调用不会重复添加 handler）

    使用 TimedRotatingFileHandler 实现每天午夜自动轮转日志文件，
    保留指定天数的日志文件。

    Args:
        log_to_file: 是否写入日志文件
        log_retention_days: 日志保留天数

    Returns:
        logger 实例
    """
    logger = logging.getLogger('typora-watch')

    # 如果已经有 handler，说明已经初始化过了，直接返回
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出（使用 TimedRotatingFileHandler 实现每日轮转）
    if log_to_file:
        # 确保日志目录存在
        os.makedirs(LOG_DIR, exist_ok=True)

        # 使用固定基础文件名，TimedRotatingFileHandler 会自动添加日期后缀
        # 例如：typora-watch.log、typora-watch.log.2024-01-01、typora-watch.log.2024-01-02
        base_log_file = os.path.join(LOG_DIR, 'typora-watch.log')

        # 创建 TimedRotatingFileHandler
        # - when='midnight': 每天午夜轮转
        # - interval=1: 每 1 天轮转一次
        # - backupCount: 保留的日志文件数量（设置为保留天数 + 1，因为包括当前文件）
        file_handler = TimedRotatingFileHandler(
            filename=base_log_file,
            when='midnight',
            interval=1,
            backupCount=log_retention_days + 1,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # 设置轮转文件的命名格式（使用 .YYYY-MM-DD 而不是默认的 .YYYY-MM-DD）
        file_handler.namer = lambda name: name.replace('.log.', '.') + '.log'

        # 设置轮转时的回调函数，用于清理旧日志
        # 注意：TimedRotatingFileHandler 会自动删除超过 backupCount 的文件

        logger.addHandler(file_handler)

    return logger


def clean_old_logs(retention_days: int = DEFAULT_LOG_RETENTION_DAYS) -> dict:
    """
    清理超过保留天数的旧日志文件

    支持两种日志文件名格式：
    - 旧格式：typora-watch-YYYY-MM-DD.log、typora-watch-error-YYYY-MM-DD.log
    - 新格式：typora-watch.log.YYYY-MM-DD（TimedRotatingFileHandler 生成）

    Args:
        retention_days: 日志保留天数

    Returns:
        清理统计：{'deleted': 数量, 'freed_bytes': 字节数}
    """
    from datetime import datetime, timedelta
    import re

    stats = {'deleted': 0, 'freed_bytes': 0}

    if not os.path.exists(LOG_DIR):
        return stats

    # 计算截止日期
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d')

    # 匹配日期的正则表达式（YYYY-MM-DD 格式）
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')

    for filename in os.listdir(LOG_DIR):
        # 只处理 typora-watch 相关的日志文件
        if not filename.startswith('typora-watch') or not filename.endswith('.log'):
            continue

        # 跳过当前日志文件（没有日期后缀的）
        if filename == 'typora-watch.log':
            continue

        # 从文件名中提取日期
        match = date_pattern.search(filename)
        if not match:
            continue

        file_date_str = match.group(1)
        try:
            file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
            if file_date < cutoff_date:
                file_path = os.path.join(LOG_DIR, filename)
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                stats['deleted'] += 1
                stats['freed_bytes'] += file_size
                get_logger().info(f'已删除旧日志: {filename}')
        except ValueError:
            # 文件名格式不正确，跳过
            pass

    if stats['deleted'] > 0:
        get_logger().info(f'日志清理完成: 删除 {stats["deleted"]} 个文件, 释放 {stats["freed_bytes"] / 1024:.1f} KB')

    return stats


# 获取 logger 实例（延迟初始化，避免与 main 中的 global 冲突）
def get_logger() -> logging.Logger:
    return logging.getLogger('typora-watch')


# 初始化日志系统
setup_logger()


# 防抖时间窗口（秒）
DEBOUNCE_SECONDS = 10


class DebounceManager:
    """
    防抖管理器，确保同一文件的同一事件在指定时间内仅触发一次

    防抖键由 (event_type, file_path) 组成，确保：
    - 同一文件的 created 事件 10 秒内只触发一次
    - 同一文件的 moved 事件 10 秒内只触发一次
    - 同一文件的 deleted 事件 10 秒内只触发一次
    - 同一文件的 modified 事件 10 秒内只触发一次
    """

    def __init__(self, debounce_seconds: float = DEBOUNCE_SECONDS):
        """
        Args:
            debounce_seconds: 防抖时间窗口（秒）
        """
        self.debounce_seconds = debounce_seconds
        # {(event_type, file_path): last_timestamp}
        self._last_processed: Dict[Tuple[str, str], float] = {}

    def should_process(self, event_type: str, file_path: str) -> bool:
        """
        检查是否应该处理该事件

        Args:
            event_type: 事件类型 ('created', 'moved', 'deleted', 'modified')
            file_path: 文件路径

        Returns:
            True 表示应该处理，False 表示在防抖期内应跳过
        """
        key = (event_type, file_path)
        current_time = time.time()

        last_time = self._last_processed.get(key, 0)
        if current_time - last_time < self.debounce_seconds:
            # 在防抖期内，跳过处理
            return False

        # 更新最后处理时间
        self._last_processed[key] = current_time
        return True

    def clear(self, file_path: str = None):
        """
        清除防抖记录

        Args:
            file_path: 如果指定，仅清除该文件的记录；否则清除所有记录
        """
        if file_path is None:
            self._last_processed.clear()
        else:
            # 清除指定文件的所有事件类型记录
            keys_to_remove = [k for k in self._last_processed if k[1] == file_path]
            for key in keys_to_remove:
                del self._last_processed[key]

    def get_info(self) -> dict:
        """获取防抖管理器状态信息"""
        return {
            'debounce_seconds': self.debounce_seconds,
            'tracked_events': len(self._last_processed),
            'events_by_type': self._count_by_type()
        }

    def _count_by_type(self) -> Dict[str, int]:
        """统计各事件类型的追踪数量"""
        counts = defaultdict(int)
        for event_type, _ in self._last_processed.keys():
            counts[event_type] += 1
        return dict(counts)


class MarkdownEventHandler:
    """Markdown 文件事件处理器（仅处理文件路径变化）"""

    def __init__(self, workspace_path: str, debounce_manager: DebounceManager = None):
        """
        Args:
            workspace_path: 工作空间路径
            debounce_manager: 防抖管理器实例
        """
        self.workspace_path = os.path.abspath(workspace_path)
        self.debounce = debounce_manager or DebounceManager()
        # 记录最近移动的文件 {dest_path: timestamp}
        # 用于防止移动后立即触发的 created 事件
        self._recently_moved: Dict[str, float] = {}

    def is_markdown_file(self, path: str) -> bool:
        """检查是否为 Markdown 文件"""
        return path.endswith('.md')

    def should_skip_file(self, path: str) -> bool:
        """
        检查文件是否应该跳过处理

        跳过条件：
        - 文件名以 "Untitled" 开头（Typora 未命名的新建文件）
        - 文件名包含 "冲突文件"

        注：备份文件（格式: test~.md）在事件处理方法中直接检查，不在此处

        Args:
            path: 文件路径

        Returns:
            True 表示应该跳过，False 表示可以处理
        """
        filename = os.path.basename(path)
        if filename.startswith('Untitled'):
            return True
        if '冲突文件' in filename:
            return True
        return False

    def _cleanup_moved_records(self, current_time: float = None):
        """
        清理过期的移动记录

        Args:
            current_time: 当前时间戳（如果为 None 则使用当前时间）
        """
        if current_time is None:
            current_time = time.time()

        expired_keys = [
            path for path, timestamp in self._recently_moved.items()
            if current_time - timestamp >= DEBOUNCE_SECONDS
        ]
        for key in expired_keys:
            del self._recently_moved[key]

    def handle_created(self, file_path: str):
        """处理新建文件"""
        # 先检查是否为备份文件（格式: test~.md）
        if os.path.basename(file_path).endswith('~.md'):
            get_logger().info(f'[忽略][新建] 临时/备份文件: {file_path}')
            return

        if not self.is_markdown_file(file_path):
            return

        current_time = time.time()

        # 检查是否应该跳过
        if self.should_skip_file(file_path):
            filename = os.path.basename(file_path)
            if filename.startswith('Untitled'):
                get_logger().info(f'[忽略][新建] Untitled 文件: {file_path}')
            elif '冲突文件' in filename:
                get_logger().info(f'[忽略][新建] 冲突文件: {file_path}')
            return

        # 检查是否为最近移动的文件（防止移动后触发 created 事件）
        moved_time = self._recently_moved.get(file_path, 0)
        if current_time - moved_time < DEBOUNCE_SECONDS:
            get_logger().debug(f'[移动-创建] 跳过移动后触发的 created 事件: {file_path}')
            # 清除移动记录（已处理，无需保留）
            self._recently_moved.pop(file_path, None)
            return

        # 清理过期的记录
        self._cleanup_moved_records(current_time)

        # 防抖检查
        if not self.debounce.should_process('created', file_path):
            get_logger().debug(f'[防抖] 跳过重复的 created 事件: {file_path}')
            return

        get_logger().info(f'检测到新建文件: {file_path}')

        try:
            modified = index_or_update_file(self.workspace_path, file_path)
            if modified:
                get_logger().info(f'  ✓ 已添加 front matter 和索引')
                # 打印更新后的 front matter 内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.startswith('---'):
                            rest = content[4:]
                            second_dash_start = rest.find('\n---')
                            if second_dash_start != -1:
                                front_matter_end = 4 + second_dash_start + 4
                                front_matter = content[:front_matter_end]
                                get_logger().info(f'  Front matter 内容:')
                                for line in front_matter.split('\n'):
                                    get_logger().info(f'    {line}')
                except Exception as e:
                    get_logger().debug(f'  读取 front matter 失败: {e}')
            else:
                get_logger().info(f'  - 跳过（已有正确的 front matter）')
        except Exception as e:
            get_logger().error(f'  ✗ 处理失败: {e}')

    def handle_moved(self, src_path: str, dest_path: str):
        """处理移动文件"""
        # 先检查是否为备份文件（格式: test~.md）
        if os.path.basename(dest_path).endswith('~.md'):
            get_logger().info(f'[忽略][移动] 临时/备份文件: {src_path} → {dest_path}')
            return

        if not self.is_markdown_file(dest_path):
            return

        # 检查是否应该跳过
        if self.should_skip_file(dest_path):
            filename = os.path.basename(dest_path)
            if filename.startswith('Untitled'):
                get_logger().info(f'[忽略][移动] Untitled 文件: {src_path} → {dest_path}')
            elif '冲突文件' in filename:
                get_logger().info(f'[忽略][移动] 冲突文件: {src_path} → {dest_path}')
            return

        get_logger().info(f'检测到文件移动: {src_path} → {dest_path}')

        try:
            # 先从索引中移除旧路径
            remove_from_index(self.workspace_path, src_path)

            # 清除源路径的防抖记录（文件已不存在）
            self.debounce.clear(src_path)

            # 记录目标路径，防止后续触发 created 事件
            self._recently_moved[dest_path] = time.time()

            # 为新路径添加 front matter（会更新 serial 的路径）
            modified = index_or_update_file(self.workspace_path, dest_path)
            if modified:
                get_logger().info(f'  ✓ 已更新索引')
            else:
                get_logger().info(f'  - 跳过（无需更新）')
        except Exception as e:
            get_logger().error(f'  ✗ 处理失败: {e}')

    def handle_deleted(self, file_path: str):
        """处理删除文件"""
        # 先检查是否为备份文件（格式: test~.md）
        if os.path.basename(file_path).endswith('~.md'):
            get_logger().info(f'[忽略][删除] 临时/备份文件: {file_path}')
            return

        if not self.is_markdown_file(file_path):
            return

        # 检查是否应该跳过
        if self.should_skip_file(file_path):
            filename = os.path.basename(file_path)
            if filename.startswith('Untitled'):
                get_logger().info(f'[忽略][删除] Untitled 文件: {file_path}')
            elif '冲突文件' in filename:
                get_logger().info(f'[忽略][删除] 冲突文件: {file_path}')
            return

        get_logger().info(f'检测到删除文件: {file_path}')

        # 防抖检查
        if not self.debounce.should_process('deleted', file_path):
            get_logger().debug(f'[防抖] 跳过重复的 deleted 事件: {file_path}')
            return

        # 直接从索引中移除
        try:
            removed = remove_from_index(self.workspace_path, file_path)
            if removed:
                get_logger().info(f'  ✓ 已从索引中移除')
            else:
                get_logger().info(f'  - 文件不在索引中')
        except Exception as e:
            get_logger().error(f'  ✗ 处理失败: {e}')

    def handle_modified(self, file_path: str):
        """处理文件修改（仅记录日志，不做操作）"""
        # 先检查是否为备份文件（格式: test~.md）
        if os.path.basename(file_path).endswith('~.md'):
            get_logger().info(f'[忽略][修改] 临时/备份文件: {file_path}')
            return

        if not self.is_markdown_file(file_path):
            return

        # 检查是否应该跳过
        if self.should_skip_file(file_path):
            filename = os.path.basename(file_path)
            if filename.startswith('Untitled'):
                get_logger().info(f'[忽略][修改] Untitled 文件: {file_path}')
            elif '冲突文件' in filename:
                get_logger().info(f'[忽略][修改] 冲突文件: {file_path}')
            return

        get_logger().info(f'检测到文件修改: {file_path}')

        # 防抖检查
        if not self.debounce.should_process('modified', file_path):
            get_logger().debug(f'[防抖] 跳过重复的 modified 事件: {file_path}')
            return

        get_logger().info(f'  仅记录日志，不做处理')


def write_pid_file(pid: int):
    """写入 PID 文件"""
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))


def read_pid_file() -> Optional[int]:
    """读取 PID 文件"""
    if not os.path.exists(PID_FILE):
        return None

    try:
        with open(PID_FILE, 'r') as f:
            return int(f.read().strip())
    except (ValueError, IOError):
        return None


def remove_pid_file():
    """删除 PID 文件"""
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def is_process_running(pid: int) -> bool:
    """检查进程是否运行"""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def stop_daemon():
    """停止后台运行的守护进程"""
    pid = read_pid_file()
    if pid is None:
        get_logger().info('未找到运行中的服务')
        return False

    if not is_process_running(pid):
        get_logger().info(f'服务已停止 (PID {pid} 不存在)')
        remove_pid_file()
        return False

    try:
        os.kill(pid, 15)  # SIGTERM
        get_logger().info(f'已发送停止信号到进程 {pid}')

        # 等待进程退出
        for _ in range(50):  # 最多等待 5 秒
            time.sleep(0.1)
            if not is_process_running(pid):
                break

        remove_pid_file()
        get_logger().info('服务已停止')
        return True
    except Exception as e:
        get_logger().error(f'停止服务失败: {e}')
        return False


def create_observer():
    """创建文件系统观察者"""
    if Observer is None:
        get_logger().error('未安装 watchdog 库，请运行: pip install watchdog')
        sys.exit(1)
    return Observer


def create_watchdog_handler(md_handler: 'MarkdownEventHandler'):
    """
    创建 watchdog 事件处理器

    延迟定义 WatchdogEventHandler 类，避免模块导入时因 watchdog 未安装而失败

    Args:
        md_handler: Markdown 事件处理器实例

    Returns:
        watchdog 事件处理器实例
    """
    from watchdog.events import FileSystemEventHandler

    class WatchdogEventHandler(FileSystemEventHandler):
        """watchdog 事件处理器适配器"""

        def __init__(self, handler):
            self.handler = handler

        def on_created(self, event):
            if not event.is_directory:
                self.handler.handle_created(event.src_path)

        def on_moved(self, event):
            if not event.is_directory:
                self.handler.handle_moved(event.src_path, event.dest_path)

        def on_deleted(self, event):
            if not event.is_directory:
                self.handler.handle_deleted(event.src_path)

        def on_modified(self, event):
            if not event.is_directory:
                self.handler.handle_modified(event.src_path)

    return WatchdogEventHandler(md_handler)


def main():
    parser = argparse.ArgumentParser(
        description='Typora 工作空间文件监控服务',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-w', '--workspace',
        default=None,
        help='工作空间路径（也可通过环境变量 TYPORA_WORKSPACE 设置）'
    )

    parser.add_argument(
        '-d', '--daemon',
        action='store_true',
        help='后台运行模式'
    )

    parser.add_argument(
        '--stop',
        action='store_true',
        help='停止后台运行的服务'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='查看服务运行状态'
    )

    parser.add_argument(
        '--no-log-file',
        action='store_true',
        help='不写入日志文件'
    )

    parser.add_argument(
        '--log-retention',
        type=int,
        default=DEFAULT_LOG_RETENTION_DAYS,
        metavar='DAYS',
        help=f'日志保留天数（默认 {DEFAULT_LOG_RETENTION_DAYS} 天）'
    )

    parser.add_argument(
        '--clean-logs',
        action='store_true',
        help='清理旧日志后退出（不启动监控）'
    )

    args = parser.parse_args()

    # 检查并安装依赖（在任何操作之前）
    check_and_install_dependencies()

    # 处理 --stop
    if args.stop:
        stop_daemon()
        return

    # 处理 --status
    if args.status:
        pid = read_pid_file()
        if pid and is_process_running(pid):
            get_logger().info(f'服务正在运行 (PID: {pid})')
            get_logger().info(f'工作空间: {os.readlink(f"/proc/{pid}/cwd") if os.path.exists(f"/proc/{pid}") else "未知"}')
        else:
            get_logger().info('服务未运行')
        return

    # 获取工作空间路径
    workspace = args.workspace or os.getenv(TYPORA_WORKSPACE_ENV)

    if not workspace:
        get_logger().error('未指定工作空间路径')
        get_logger().error('请通过以下方式之一指定：')
        get_logger().error(f'  1. 命令行参数: -w /path/to/workspace')
        get_logger().error(f'  2. 环境变量: export {TYPORA_WORKSPACE_ENV}=/path/to/workspace')
        sys.exit(1)

    workspace = os.path.abspath(workspace)

    if not os.path.isdir(workspace):
        get_logger().error(f'工作空间路径不存在: {workspace}')
        sys.exit(1)

    # 处理 --clean-logs（仅清理日志，不启动监控）
    if args.clean_logs:
        get_logger().info(f'日志保留天数: {args.log_retention}')
        get_logger().info(f'日志目录: {LOG_DIR}')
        get_logger().info('')
        stats = clean_old_logs(args.log_retention)
        get_logger().info(f'\n清理完成: 删除 {stats["deleted"]} 个文件, 释放 {stats["freed_bytes"] / 1024:.1f} KB')
        sys.exit(0)

    # 检查是否已有实例运行
    existing_pid = read_pid_file()
    if existing_pid and is_process_running(existing_pid):
        get_logger().warning(f'服务已在运行 (PID: {existing_pid})')
        get_logger().info('如需重启，请先使用 --stop 停止现有服务')
        sys.exit(1)

    # 后台运行
    if args.daemon:
        if sys.platform == 'win32':
            get_logger().error('Windows 系统请使用 NSSM 或任务计划程序安装为服务')
            get_logger().info('参考文档: service-install/windows-nssm.md')
            sys.exit(1)
        else:
            # Unix-like 系统：使用 fork
            pid = os.fork()
            if pid > 0:
                # 父进程退出
                get_logger().info(f'服务已在后台启动 (PID: {pid})')
                write_pid_file(pid)
                sys.exit(0)

            # 子进程继续
            os.setsid()
            os.umask(0)

    # 设置日志（重新初始化以应用命令行参数）
    setup_logger(log_to_file=not args.no_log_file, log_retention_days=args.log_retention)

    # 写入 PID（前台模式也需要）
    atexit.register(remove_pid_file)
    write_pid_file(os.getpid())

    get_logger().info('=' * 50)
    get_logger().info('Typora 工作空间文件监控服务')
    get_logger().info('=' * 50)
    get_logger().info(f'工作空间: {workspace}')
    get_logger().info(f'PID: {os.getpid()}')
    get_logger().info(f'日志目录: {LOG_DIR}')
    get_logger().info(f'日志文件: typora-watch.log (自动按日期轮转)')
    get_logger().info(f'日志保留: {args.log_retention} 天')
    get_logger().info(f'防抖窗口: {DEBOUNCE_SECONDS} 秒')
    get_logger().info('')

    # 创建防抖管理器和事件处理器
    debounce_manager = DebounceManager(debounce_seconds=DEBOUNCE_SECONDS)
    md_handler = MarkdownEventHandler(workspace, debounce_manager=debounce_manager)

    # 创建 watchdog 事件处理器和观察者
    ObserverClass = create_observer()
    watchdog_handler = create_watchdog_handler(md_handler)

    # 创建观察者
    observer = ObserverClass()
    observer.schedule(watchdog_handler, workspace, recursive=True)

    # 启动监控
    observer.start()
    get_logger().info('监控已启动，等待文件变化...')
    get_logger().info('按 Ctrl+C 停止服务')
    get_logger().info('')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        get_logger().info('')
        get_logger().info('收到停止信号，正在关闭...')
        observer.stop()
        observer.join()
        get_logger().info('服务已停止')


if __name__ == '__main__':
    main()
