#!/usr/bin/env python3
"""
测试 watchdog 是否能正常工作
"""

import os
import sys
import time
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

workspace = "/Users/laomst/__baidu_sync_disk__/__typora_workspace__2"


class TestHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"[CREATED] {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            print(f"[MODIFIED] {event.src_path}")

    def on_moved(self, event):
        if not event.is_directory:
            print(f"[MOVED] {event.src_path} -> {event.dest_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"[DELETED] {event.src_path}")


print(f"监控目录: {workspace}")
print("创建一个 .md 文件来测试...")
print("按 Ctrl+C 退出\n")

observer = Observer()
observer.schedule(TestHandler(), workspace, recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    observer.join()
    print("\n已停止")
