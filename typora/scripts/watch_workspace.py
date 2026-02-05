#!/usr/bin/env python3
"""
Typora 工作空间文件监控服务

监控工作空间中的 Markdown 文件变化，自动触发索引更新。

监控事件：
- 新建 .md 文件 → 自动添加 front matter 和索引
- 移动 .md 文件 → 自动更新 typora-root-url 和索引
- 删除 .md 文件 → 从索引中移除

使用方式：
    # 手动运行（前台）
    python watch_workspace.py

    # 指定工作空间路径
    python watch_workspace.py -w /path/to/workspace

    # 后台运行
    python watch_workspace.py --daemon

    # 停止后台运行
    python watch_workspace.py --stop

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
from pathlib import Path
from typing import Optional

# 环境变量名称
TYPORA_WORKSPACE_ENV = 'TYPORA_WORKSPACE'

# PID 文件路径（用于后台运行管理）
PID_FILE = os.path.expanduser('~/.typora-ext-watch.pid')

# 日志目录
LOG_DIR = os.path.expanduser('~/.typora-ext-logs')
# 日志文件保留天数（默认 30 天）
DEFAULT_LOG_RETENTION_DAYS = 30


def get_log_file_path(log_type: str = 'log') -> str:
    """
    获取按日期命名的日志文件路径

    Args:
        log_type: 日志类型 ('log' 或 'error')

    Returns:
        日志文件的完整路径
    """
    from datetime import datetime
    date_str = datetime.now().strftime('%Y-%m-%d')
    if log_type == 'error':
        filename = f'typora-watch-error-{date_str}.log'
    else:
        filename = f'typora-watch-{date_str}.log'
    return os.path.join(LOG_DIR, filename)

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


def setup_logger(log_to_file: bool = True) -> logging.Logger:
    """设置日志系统（幂等性：多次调用不会重复添加 handler）"""
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

    # 文件输出（按日期命名）
    if log_to_file:
        # 确保日志目录存在
        os.makedirs(LOG_DIR, exist_ok=True)

        # 普通日志
        log_file = get_log_file_path('log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def clean_old_logs(retention_days: int = DEFAULT_LOG_RETENTION_DAYS) -> dict:
    """
    清理超过保留天数的旧日志文件

    Args:
        retention_days: 日志保留天数

    Returns:
        清理统计：{'deleted': 数量, 'freed_bytes': 字节数}
    """
    from datetime import datetime, timedelta

    stats = {'deleted': 0, 'freed_bytes': 0}

    if not os.path.exists(LOG_DIR):
        return stats

    # 计算截止日期
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d')

    for filename in os.listdir(LOG_DIR):
        # 只处理日志文件
        if not (filename.startswith('typora-watch-') and filename.endswith('.log')):
            continue

        # 从文件名提取日期
        # 格式: typora-watch-YYYY-MM-DD.log 或 typora-watch-error-YYYY-MM-DD.log
        parts = filename.replace('typora-watch-', '').replace('.log', '').split('-')
        if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
            file_date_str = f'{parts[0]}-{parts[1]}-{parts[2]}'
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


class MarkdownEventHandler:
    """Markdown 文件事件处理器（仅处理文件路径变化）"""

    def __init__(self, workspace_path: str):
        """
        Args:
            workspace_path: 工作空间路径
        """
        self.workspace_path = os.path.abspath(workspace_path)

    def is_markdown_file(self, path: str) -> bool:
        """检查是否为 Markdown 文件"""
        return path.endswith('.md')

    def handle_created(self, file_path: str):
        """处理新建文件"""
        if not self.is_markdown_file(file_path):
            return

        get_logger().info(f'检测到新建文件: {file_path}')

        try:
            modified = index_or_update_file(self.workspace_path, file_path)
            if modified:
                get_logger().info(f'  ✓ 已添加 front matter 和索引')
            else:
                get_logger().info(f'  - 跳过（已有正确的 front matter）')
        except Exception as e:
            get_logger().error(f'  ✗ 处理失败: {e}')

    def handle_moved(self, src_path: str, dest_path: str):
        """处理移动文件"""
        if not self.is_markdown_file(dest_path):
            return

        get_logger().info(f'检测到文件移动: {src_path} → {dest_path}')

        try:
            # 先从索引中移除旧路径
            remove_from_index(self.workspace_path, src_path)

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
        if not self.is_markdown_file(file_path):
            return

        get_logger().info(f'检测到删除文件: {file_path}')

        try:
            removed = remove_from_index(self.workspace_path, file_path)
            if removed:
                get_logger().info(f'  ✓ 已从索引中移除')
            else:
                get_logger().info(f'  - 文件不在索引中')
        except Exception as e:
            get_logger().error(f'  ✗ 处理失败: {e}')


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


class WatchdogEventHandler(FileSystemEventHandler):
    """watchdog 事件处理器适配器（仅处理文件路径变化）"""

    def __init__(self, handler: MarkdownEventHandler):
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
    setup_logger(log_to_file=not args.no_log_file)

    # 写入 PID（前台模式也需要）
    atexit.register(remove_pid_file)
    write_pid_file(os.getpid())

    get_logger().info('=' * 50)
    get_logger().info('Typora 工作空间文件监控服务')
    get_logger().info('=' * 50)
    get_logger().info(f'工作空间: {workspace}')
    get_logger().info(f'PID: {os.getpid()}')
    get_logger().info(f'日志目录: {LOG_DIR}')
    get_logger().info(f'当前日志: {os.path.basename(get_log_file_path())}')
    get_logger().info('')

    # 创建事件处理器
    md_handler = MarkdownEventHandler(workspace)

    # 创建 watchdog 事件处理器和观察者
    ObserverClass = create_observer()
    watchdog_handler = WatchdogEventHandler(md_handler)

    # 创建观察者
    observer = ObserverClass()
    observer.schedule(watchdog_handler, workspace, recursive=True)

    # 启动前清理旧日志
    get_logger().info(f'清理旧日志（保留 {args.log_retention} 天）...')
    try:
        clean_old_logs(args.log_retention)
    except Exception as e:
        get_logger().error(f'日志清理失败: {e}')

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
