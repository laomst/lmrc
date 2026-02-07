#!/usr/bin/env python3
"""
Typora Markdown 文件索引模块

为 Markdown 文件添加 YAML front matter 并维护索引文件。

## 公共 API

该模块对外提供以下标准函数：

- index_or_update_file(workspace_path: str, file_path: str) -> bool
    为单个 Markdown 文件初始化或更新 front matter 和索引。

- remove_from_index(workspace_path: str, file_path: str) -> bool
    从索引中移除指定文件（用于文件删除事件）。

## 使用示例

```python
from index_typora_markdowns import index_or_update_file, remove_from_index

# 初始化或更新文件索引
modified = index_or_update_file('/path/to/workspace', '/path/to/workspace/note.md')

# 从索引中移除文件
removed = remove_from_index('/path/to/workspace', '/path/to/workspace/note.md')
```

## 命令行使用

    # 处理单个文件
    python index_typora_markdowns.py -w /workspace file.md

    # 处理目录
    python index_typora_markdowns.py -w /workspace directory/

    # 处理多个路径
    python index_typora_markdowns.py file1.md file2.md dir/
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Tuple

from util.logger import write_log

# 环境变量名称
TYPORA_WORKSPACE_ENV = 'TYPORA_WORKSPACE'


def _find_files_by_extension(directory: str, extension: str) -> list[str]:
    """递归查找指定目录下所有指定扩展名的文件"""
    file_list = []
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.endswith(f'.{extension}'):
            file_list.append(entry.path)
        elif entry.is_dir():
            file_list.extend(_find_files_by_extension(entry.path, extension))
    return file_list


def _generate_serial() -> str:
    """生成8位唯一标识符，首位字母，其余7位字母数字混合"""
    letters = 'abcdefghijklmnopqrstuvwxyz'
    alnum = letters + '0123456789'
    # 第一位从 26 个小写字母中随机选择
    first_char = random.choice(letters)
    # 其余 7 位从 36 个字符（26字母+10数字）中随机选择
    remaining = ''.join(random.choice(alnum) for _ in range(7))
    return first_char + remaining


def _generate_unique_serial(workspace_path: str) -> str:
    """
    生成唯一的 serial，确保不在索引文件中重复

    Args:
        workspace_path: 工作空间路径

    Returns:
        唯一的8位 serial
    """
    index_path = _get_index_file_path(workspace_path)
    index_data = _read_index_file(index_path)

    while True:
        serial = _generate_serial()
        if serial not in index_data:
            return serial
        # 如果已存在，继续循环生成新的


def _calculate_relative_path(workspace_path: str, file_path: str) -> str:
    """
    计算文件相对于工作空间的 ../ 形式路径
    例如: /workspace/__laomst_blogs__/000-AI编程专题/file.md -> ../../
    """
    abs_workspace = os.path.abspath(workspace_path)
    abs_file = os.path.abspath(file_path)

    if not abs_file.startswith(abs_workspace):
        raise ValueError(f'文件 {file_path} 不在工作空间 {workspace_path} 内')

    # 获取文件所在目录相对于工作空间的深度
    relative = abs_file[len(abs_workspace):].lstrip(os.sep)
    # 去掉文件名，只保留目录部分
    dir_path = os.path.dirname(relative)

    # 计算需要向上几级（目录深度）
    if dir_path == '.' or dir_path == '':
        return ''

    depth = len([p for p in dir_path.split(os.sep) if p])
    return '../' * depth


def _has_front_matter(content: str) -> bool:
    """检查文件是否已有 YAML front matter"""
    return content.startswith('---')


def _get_existing_front_matter(content: str) -> Optional[Tuple[str, str]]:
    """
    获取现有的 front matter
    返回: (front_matter, remaining_content) 或 None
    """
    if not content.startswith('---'):
        return None

    # 查找第二个 ---（跳过开头的 ---）
    # 第二个 --- 的位置应该在 content[4:] 中查找
    rest = content[4:]
    second_dash_start = rest.find('\n---')

    if second_dash_start == -1:
        return None

    # 第二个 --- 在 content 中的结束位置（包含 --- 和前面的换行符）
    front_matter_end = 4 + second_dash_start + 4

    front_matter = content[:front_matter_end]
    remaining_content = content[front_matter_end:].lstrip('\n')
    return front_matter, remaining_content


def _parse_front_matter(front_matter: str) -> dict:
    """
    解析 front matter 为字典
    保留所有字段
    """
    fields = {}
    # 跳过开头的 --- 和结尾的 ---
    lines = front_matter.split('\n')
    for line in lines[1:-1]:  # 跳过第一个 --- 和最后一个 ---
        line = line.strip()
        if line and ':' in line:
            key, value = line.split(':', 1)
            fields[key.strip()] = value.strip()
    return fields


def _build_front_matter(fields: dict) -> str:
    """
    从字典构建 front matter 字符串
    确保没有末尾空行
    """
    lines = ['---']
    for key, value in fields.items():
        lines.append(f'{key}: {value}')
    lines.append('---')
    return '\n'.join(lines)


def _extract_serial_from_front_matter(front_matter: str) -> Optional[str]:
    """从现有的 front matter 中提取 serial"""
    fields = _parse_front_matter(front_matter)
    serial = fields.get('serial', '')
    # 只需判断 serial 非空
    if serial and serial.strip():
        return serial
    return None


def _extract_typora_root_url_from_front_matter(front_matter: str) -> Optional[str]:
    """从现有的 front matter 中提取 typora-root-url"""
    fields = _parse_front_matter(front_matter)
    return fields.get('typora-root-url')


def _create_front_matter(serial: str, relative_path: str) -> str:
    """创建新的 front matter"""
    # typora-root-url 拼接规则: 相对路径
    typora_root_url = relative_path

    # typora-copy-images-to 拼接规则: 相对路径 + .assets/ + uuid首位 + / + 完整uuid
    url_prefix = serial[:1]
    if relative_path:
        typora_copy_images_to = f'{relative_path}.assets/{url_prefix}/{serial}'
    else:
        typora_copy_images_to = f'.assets/{url_prefix}/{serial}'

    # 使用 _build_front_matter 确保格式一致
    fields = {
        'serial': serial,
        'typora-root-url': typora_root_url,
        'typora-copy-images-to': typora_copy_images_to,
    }
    return _build_front_matter(fields)


def _calculate_file_relative_path(workspace_path: str, file_path: str) -> str:
    """
    计算文件相对于工作空间的路径（以 / 开头）
    例如: /workspace/vibe-coding/file.md -> /vibe-coding/file.md
    """
    abs_workspace = os.path.abspath(workspace_path)
    abs_file = os.path.abspath(file_path)

    if not abs_file.startswith(abs_workspace):
        raise ValueError(f'文件 {file_path} 不在工作空间 {workspace_path} 内')

    # 获取文件相对于工作空间的路径
    relative = abs_file[len(abs_workspace):]
    # 确保以 / 开头
    if not relative.startswith('/'):
        relative = '/' + relative
    return relative


def _get_index_file_path(workspace_path: str) -> str:
    """获取索引文件路径（工作空间根目录下的 .index/path_index.json）"""
    return os.path.join(workspace_path, '.index', 'path_index.json')


def _read_index_file(index_path: str) -> dict:
    """读取索引文件，如果不存在返回空字典"""
    if not os.path.exists(index_path):
        return {}
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        write_log(f'警告: 索引文件格式错误，将创建新的索引文件')
        return {}


def _write_index_file(index_path: str, index_data: dict) -> None:
    """写入索引文件"""
    # 确保目录存在
    index_dir = os.path.dirname(index_path)
    if index_dir and not os.path.exists(index_dir):
        os.makedirs(index_dir, exist_ok=True)
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)


def _update_index(workspace_path: str, serial: str, file_path: str) -> None:
    """
    更新索引文件，添加或更新指定 serial 的记录

    Args:
        workspace_path: 工作空间路径
        serial: 文章的 serial
        file_path: markdown 文件的绝对路径
    """
    index_path = _get_index_file_path(workspace_path)

    # 读取现有索引
    index_data = _read_index_file(index_path)

    # 计算文件的相对路径
    local_path = _calculate_file_relative_path(workspace_path, file_path)

    # 更新索引（简化结构：serial 直接对应 localPath）
    index_data[serial] = local_path

    # 写回索引文件
    _write_index_file(index_path, index_data)


def _add_front_matter_to_file(file_path: str, workspace_path: str) -> bool:
    """
    为单个文件添加或更新 front matter
    返回: 是否进行了修改

    逻辑:
    1. 无 matter -> 全量补充
    2. 有 matter 但无 serial -> 生成 serial，重新计算 typora-root-url，保留其他字段
    3. 有 matter 且有 serial -> 保留 serial 和其他字段，重新计算 typora-root-url
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    relative_path = _calculate_relative_path(workspace_path, file_path)

    if _has_front_matter(content):
        # 有 front matter，解析并保留所有字段
        existing = _get_existing_front_matter(content)
        if not existing:
            return False

        front_matter, remaining = existing
        fields = _parse_front_matter(front_matter)
        existing_serial = _extract_serial_from_front_matter(front_matter)
        existing_url = fields.get('typora-root-url')
        existing_copy_url = fields.get('typora-copy-images-to')

        # 计算新的 typora-root-url 和 typora-copy-images-to
        if existing_serial:
            # 使用现有的 serial 计算新的值
            new_typora_root_url = relative_path
            url_prefix = existing_serial[:1]
            if relative_path:
                new_typora_copy_images_to = f'{relative_path}.assets/{url_prefix}/{existing_serial}'
            else:
                new_typora_copy_images_to = f'.assets/{url_prefix}/{existing_serial}'

            # 检查是否需要更新 front matter
            if existing_url == new_typora_root_url and existing_copy_url == new_typora_copy_images_to:
                # front matter 无需更新，但要确保文件在索引中
                write_log(f'  front matter 无需更新，检查索引...')
                _update_index(workspace_path, existing_serial, file_path)
                return False

            # 更新 typora-root-url 和 typora-copy-images-to，保留所有其他字段
            fields['typora-root-url'] = new_typora_root_url
            fields['typora-copy-images-to'] = new_typora_copy_images_to
            new_front_matter = _build_front_matter(fields)

            new_content = new_front_matter + '\n\n' + remaining

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # 更新索引
            _update_index(workspace_path, existing_serial, file_path)

            write_log(f'  更新 typora-root-url 和 typora-copy-images-to: serial={existing_serial}')
            return True
        else:
            # 没有 serial，生成新的，保留所有其他字段
            serial = _generate_unique_serial(workspace_path)
            fields['serial'] = serial

            # 计算 typora-root-url 和 typora-copy-images-to
            typora_root_url = relative_path
            url_prefix = serial[:1]
            if relative_path:
                typora_copy_images_to = f'{relative_path}.assets/{url_prefix}/{serial}'
            else:
                typora_copy_images_to = f'.assets/{url_prefix}/{serial}'
            fields['typora-root-url'] = typora_root_url
            fields['typora-copy-images-to'] = typora_copy_images_to

            new_front_matter = _build_front_matter(fields)
            new_content = new_front_matter + '\n\n' + remaining

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # 更新索引
            _update_index(workspace_path, serial, file_path)

            write_log(f'  添加 serial、typora-root-url 和 typora-copy-images-to: serial={serial} (保留其他字段)')
            return True
    else:
        # 没有 front matter，添加新的
        serial = _generate_unique_serial(workspace_path)
        new_front_matter = _create_front_matter(serial, relative_path)

        new_content = new_front_matter + '\n\n' + content

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # 更新索引
        _update_index(workspace_path, serial, file_path)

        write_log(f'  添加 front matter: serial={serial}')
        return True


def _collect_markdown_files(paths: list[str], workspace_path: str) -> list[str]:
    """
    收集所有需要处理的 markdown 文件
    支持文件路径和目录路径混合

    Args:
        paths: 要处理的文件或目录路径列表
        workspace_path: 工作空间路径

    Returns:
        符合条件的 markdown 文件列表
    """
    abs_workspace = os.path.abspath(workspace_path)
    md_files = []

    for path in paths:
        abs_path = os.path.abspath(path)

        if not os.path.exists(abs_path):
            write_log(f'警告: 路径不存在，跳过: {path}')
            continue

        # 校验路径是否在工作空间内或就是工作空间本身
        # 规范化路径后进行比较（去除末尾的分隔符）
        normalized_path = abs_path.rstrip(os.sep)
        normalized_workspace = abs_workspace.rstrip(os.sep)

        if normalized_path != normalized_workspace and not normalized_path.startswith(normalized_workspace + os.sep):
            write_log(f'错误: 路径不在工作空间内，跳过: {path}')
            write_log(f'  工作空间: {abs_workspace}')
            continue

        if os.path.isfile(abs_path):
            # 是文件
            if abs_path.endswith('.md'):
                md_files.append(abs_path)
            else:
                write_log(f'警告: 非 Markdown 文件，跳过: {path}')
        elif os.path.isdir(abs_path):
            # 是目录，递归查找所有 .md 文件
            found = _find_files_by_extension(abs_path, 'md')
            md_files.extend(found)
        else:
            write_log(f'警告: 无法识别的路径类型，跳过: {path}')

    return md_files


def main():
    parser = argparse.ArgumentParser(
        description='为 Markdown 文件添加或更新 YAML front matter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  %(prog)s file.md                           # 处理单个文件
  %(prog)s directory/                        # 处理目录
  %(prog)s file1.md file2.md dir/            # 处理多个路径
  %(prog)s -w /workspace file.md             # 指定工作空间路径
        '''
    )

    parser.add_argument(
        'paths',
        nargs='*',
        help='要处理的文件或目录路径（可指定多个）'
    )

    parser.add_argument(
        '-w', '--workspace',
        default=None,
        help='工作空间路径（也可通过环境变量 TYPORA_WORKSPACE 设置）'
    )

    args = parser.parse_args()

    # 获取工作空间路径：优先命令行参数，其次环境变量
    workspace = args.workspace or os.getenv(TYPORA_WORKSPACE_ENV)

    if not workspace:
        write_log(f'错误: 未指定工作空间路径')
        write_log(f'请通过以下方式之一指定：')
        write_log(f'  1. 命令行参数: -w /path/to/workspace')
        write_log(f'  2. 环境变量: export {TYPORA_WORKSPACE_ENV}=/path/to/workspace')
        sys.exit(1)

    workspace = os.path.abspath(workspace)

    if not os.path.isdir(workspace):
        write_log(f'错误: 工作空间路径不存在: {workspace}')
        sys.exit(1)

    # 检查是否指定了要处理的路径
    if not args.paths:
        write_log('错误: 未指定要处理的文件或目录')
        write_log('使用 --help 查看帮助信息')
        sys.exit(1)

    # 收集所有需要处理的 markdown 文件
    md_files = _collect_markdown_files(args.paths, workspace)

    if not md_files:
        write_log('未找到任何 Markdown 文件')
        sys.exit(0)

    # 去重
    md_files = list(set(md_files))
    md_files.sort()

    write_log(f'工作空间: {workspace}')
    write_log(f'找到 {len(md_files)} 个 Markdown 文件\n')

    added_count = 0
    skipped_count = 0
    error_count = 0

    for md_file in md_files:
        # 尝试计算相对路径用于显示
        try:
            relative_path = _calculate_relative_path(workspace, md_file)
            write_log(f'处理: {relative_path}')
        except ValueError:
            # 文件不在工作空间内，显示绝对路径
            write_log(f'处理: {md_file} (警告: 文件不在工作空间内)')

        try:
            modified = _add_front_matter_to_file(md_file, workspace)
            if modified:
                added_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            write_log(f'  错误: {e}')
            error_count += 1

    write_log(f'\n处理完成!')
    write_log(f'  添加/更新: {added_count} 个文件')
    write_log(f'  跳过: {skipped_count} 个文件')
    write_log(f'  错误: {error_count} 个文件')


# ==============================================================================
# 公共 API - 以下函数供外部模块调用（如 watch_workspace.py）
# ==============================================================================

def index_or_update_file(workspace_path: str, file_path: str) -> bool:
    """
    为 Markdown 文件初始化或更新 front matter 和索引

    这是模块的主要公共 API 函数，供外部调用以：
    1. 验证文件是否在工作空间内
    2. 为文件添加或更新 YAML front matter
    3. 更新工作空间根目录下的 .index/path_index.json 索引

    Args:
        workspace_path: 工作空间目录的绝对路径
        file_path: 被操作的 Markdown 文件的绝对路径

    Returns:
        bool: 是否进行了修改（True=已修改，False=无需修改）

    Raises:
        ValueError: 文件不在工作空间内
        FileNotFoundError: 文件不存在
        Exception: 其他处理错误

    示例:
        >>> index_or_update_file('/workspace', '/workspace/notes/test.md')
        True
    """
    # 规范化路径
    abs_workspace = os.path.abspath(workspace_path)
    abs_file = os.path.abspath(file_path)

    # 验证工作空间是否存在
    if not os.path.isdir(abs_workspace):
        raise ValueError(f'工作空间路径不存在: {abs_workspace}')

    # 验证文件是否存在
    if not os.path.isfile(abs_file):
        raise FileNotFoundError(f'文件不存在: {abs_file}')

    # 验证文件是否在工作空间内
    normalized_file = abs_file.rstrip(os.sep)
    normalized_workspace = abs_workspace.rstrip(os.sep)

    if normalized_file != normalized_workspace and not normalized_file.startswith(normalized_workspace + os.sep):
        raise ValueError(f'文件不在工作空间内: file={abs_file}, workspace={abs_workspace}')

    # 验证是否为 Markdown 文件
    if not abs_file.endswith('.md'):
        raise ValueError(f'文件不是 Markdown 文件: {abs_file}')

    # 调用内部函数处理
    return _add_front_matter_to_file(abs_file, abs_workspace)


def _remove_assets_dir(workspace_path: str, serial: str) -> bool:
    """
    删除指定 serial 对应的 assets 目录

    assets 目录路径规则: {工作空间目录}/.assets/{serial首位}/{serial}

    Args:
        workspace_path: 工作空间目录的绝对路径
        serial: 文章的 serial（8位标识符）

    Returns:
        bool: 是否成功删除（True=已删除，False=目录不存在）
    """
    url_prefix = serial[:1]
    assets_dir = os.path.join(workspace_path, '.assets', url_prefix, serial)

    if os.path.isdir(assets_dir):
        try:
            import shutil
            shutil.rmtree(assets_dir)
            write_log(f'  已删除 assets 目录: {assets_dir}')
            return True
        except Exception as e:
            write_log(f'  删除 assets 目录失败: {e}')
            return False

    return False


def remove_from_index(workspace_path: str, file_path: str) -> bool:
    """
    从索引中移除指定的 Markdown 文件

    当文件被删除或移动时，从工作空间根目录的 .index/path_index.json 中移除其索引，
    并删除对应的 assets 目录。

    Args:
        workspace_path: 工作空间目录的绝对路径
        file_path: 被移除的 Markdown 文件的绝对路径

    Returns:
        bool: 是否成功移除（True=已移除，False=文件不在索引中）

    Raises:
        ValueError: 工作空间路径不存在

    示例:
        >>> remove_from_index('/workspace', '/workspace/notes/test.md')
        True
    """
    abs_workspace = os.path.abspath(workspace_path)
    abs_file = os.path.abspath(file_path)

    # 验证工作空间是否存在
    if not os.path.isdir(abs_workspace):
        raise ValueError(f'工作空间路径不存在: {abs_workspace}')

    index_path = _get_index_file_path(abs_workspace)
    index_data = _read_index_file(index_path)

    # 计算文件的相对路径
    try:
        relative_path = _calculate_file_relative_path(abs_workspace, abs_file)
    except ValueError:
        # 文件不在工作空间内，无法移除
        return False

    # 查找并移除该文件的索引
    removed = False
    to_delete = []

    for serial, path in index_data.items():
        if path == relative_path:
            to_delete.append(serial)
            removed = True

    # 先删除 assets 目录，再从索引中移除
    for serial in to_delete:
        _remove_assets_dir(abs_workspace, serial)
        del index_data[serial]

    if removed:
        _write_index_file(index_path, index_data)

    return removed


# 定义公共 API（__all__ 用于控制 from module import * 的行为）
__all__ = [
    'index_or_update_file',
    'remove_from_index',
    'TYPORA_WORKSPACE_ENV',
]


if __name__ == '__main__':
    main()
