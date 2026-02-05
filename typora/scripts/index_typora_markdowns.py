#!/usr/bin/env python3
"""
为 Typora 工作空间中的所有 Markdown 文件添加 YAML front matter 并维护索引

生成的 front matter 包含：
- serial: 随机生成的 8 位 UUID（从32位UUID截取前8位）
- typora-root-url: ../形式相对路径
- typora-copy-images-to: ../形式相对路径 + .assets/ + UUID前2位 + "/" + 完整UUID

例如：
  typora-root-url: ../../
  typora-copy-images-to: ../../.assets/38/38b1fe14

索引文件：
- 工作空间根目录下的 .index.json
- 结构：{"serial": "/相对路径/文件.md"}
- 例如：{"38b1fe14": "/vibe-coding/spec-driven-development.md"}

工作空间配置：
    通过以下两种方式之一指定工作空间路径（优先级从高到低）：
    1. 命令行参数: -w /path/to/workspace
    2. 环境变量: export TYPORA_WORKSPACE=/path/to/workspace

使用方式:
    # 处理单个文件（使用环境变量配置的工作空间）
    python index_typora_markdowns.py path/to/file.md

    # 处理目录（使用环境变量配置的工作空间）
    python index_typora_markdowns.py path/to/directory

    # 指定工作空间路径
    python index_typora_markdowns.py -w /path/to/workspace path/to/file.md

    # 处理多个路径（文件或目录混合）
    python index_typora_markdowns.py file1.md dir1/ file2.md dir2/
"""

import argparse
import json
import os
import re
import sys
import uuid
from typing import Optional, Tuple

from util.logger import write_log

# 环境变量名称
TYPORA_WORKSPACE_ENV = 'TYPORA_WORKSPACE'


def find_files_by_extension(directory: str, extension: str) -> list[str]:
    """递归查找指定目录下所有指定扩展名的文件"""
    file_list = []
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.endswith(f'.{extension}'):
            file_list.append(entry.path)
        elif entry.is_dir():
            file_list.extend(find_files_by_extension(entry.path, extension))
    return file_list


def generate_serial() -> str:
    """生成8位UUID（从32位UUID截取前8位）"""
    return uuid.uuid4().hex[:8]


def generate_unique_serial(workspace_path: str) -> str:
    """
    生成唯一的 serial，确保不在索引文件中重复

    Args:
        workspace_path: 工作空间路径

    Returns:
        唯一的8位 serial
    """
    index_path = get_index_file_path(workspace_path)
    index_data = read_index_file(index_path)

    while True:
        serial = generate_serial()
        if serial not in index_data:
            return serial
        # 如果已存在，继续循环生成新的


def calculate_relative_path(workspace_path: str, file_path: str) -> str:
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


def has_front_matter(content: str) -> bool:
    """检查文件是否已有 YAML front matter"""
    return content.startswith('---')


def get_existing_front_matter(content: str) -> Optional[Tuple[str, str]]:
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


def parse_front_matter(front_matter: str) -> dict:
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


def build_front_matter(fields: dict) -> str:
    """
    从字典构建 front matter 字符串
    确保没有末尾空行
    """
    lines = ['---']
    for key, value in fields.items():
        lines.append(f'{key}: {value}')
    lines.append('---')
    return '\n'.join(lines)


def extract_serial_from_front_matter(front_matter: str) -> Optional[str]:
    """从现有的 front matter 中提取 serial"""
    fields = parse_front_matter(front_matter)
    serial = fields.get('serial', '')
    # 验证是否为8位16进制字符串
    if re.match(r'^[a-f0-9]{8}$', serial, re.IGNORECASE):
        return serial
    return None


def extract_typora_root_url_from_front_matter(front_matter: str) -> Optional[str]:
    """从现有的 front matter 中提取 typora-root-url"""
    fields = parse_front_matter(front_matter)
    return fields.get('typora-root-url')


def create_front_matter(serial: str, relative_path: str) -> str:
    """创建新的 front matter"""
    # typora-root-url 拼接规则: 相对路径
    typora_root_url = relative_path

    # typora-copy-images-to 拼接规则: 相对路径 + .assets/ + uuid前2位 + / + 完整uuid
    url_prefix = serial[:2]
    if relative_path:
        typora_copy_images_to = f'{relative_path}.assets/{url_prefix}/{serial}'
    else:
        typora_copy_images_to = f'.assets/{url_prefix}/{serial}'

    # 使用 build_front_matter 确保格式一致
    fields = {
        'serial': serial,
        'typora-root-url': typora_root_url,
        'typora-copy-images-to': typora_copy_images_to
    }
    return build_front_matter(fields)


def calculate_file_relative_path(workspace_path: str, file_path: str) -> str:
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


def get_index_file_path(workspace_path: str) -> str:
    """获取索引文件路径（工作空间根目录下的 .index.json）"""
    return os.path.join(workspace_path, '.index.json')


def read_index_file(index_path: str) -> dict:
    """读取索引文件，如果不存在返回空字典"""
    if not os.path.exists(index_path):
        return {}
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        write_log(f'警告: 索引文件格式错误，将创建新的索引文件')
        return {}


def write_index_file(index_path: str, index_data: dict) -> None:
    """写入索引文件"""
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)


def update_index(workspace_path: str, serial: str, file_path: str) -> None:
    """
    更新索引文件，添加或更新指定 serial 的记录

    Args:
        workspace_path: 工作空间路径
        serial: 文章的 serial
        file_path: markdown 文件的绝对路径
    """
    index_path = get_index_file_path(workspace_path)

    # 读取现有索引
    index_data = read_index_file(index_path)

    # 计算文件的相对路径
    local_path = calculate_file_relative_path(workspace_path, file_path)

    # 更新索引（简化结构：serial 直接对应 localPath）
    index_data[serial] = local_path

    # 写回索引文件
    write_index_file(index_path, index_data)


def verify_and_fix_index(workspace_path: str, auto_fix: bool = True) -> dict:
    """
    验证索引完整性并修复错误的路径

    检查每个 serial 对应的文件是否存在：
    - 如果存在：验证路径是否正确
    - 如果不存在：在工作空间中搜索该文件（通过 serial），更新索引
    - 如果找不到：从索引中移除

    Args:
        workspace_path: 工作空间路径
        auto_fix: 是否自动修复错误的索引

    Returns:
        统计信息：{'verified': 数量, 'fixed': 数量, 'removed': 数量, 'errors': 列表}
    """
    index_path = get_index_file_path(workspace_path)
    index_data = read_index_file(index_path)

    stats = {
        'verified': 0,
        'fixed': 0,
        'removed': 0,
        'errors': []
    }

    if not index_data:
        return stats

    write_log('开始验证索引完整性...')

    # 需要更新的索引
    to_update = {}
    # 需要移除的 serial
    to_remove = []

    for serial, indexed_path in index_data.items():
        # 构建绝对路径
        abs_indexed_path = os.path.join(workspace_path, indexed_path.lstrip('/'))

        if os.path.exists(abs_indexed_path):
            # 文件存在，验证是否是正确的文件（检查 serial）
            try:
                with open(abs_indexed_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    front_matter = get_existing_front_matter(content)
                    if front_matter:
                        file_serial = extract_serial_from_front_matter(front_matter[0])
                        if file_serial == serial:
                            stats['verified'] += 1
                        else:
                            # 文件存在但 serial 不匹配，记录错误
                            stats['errors'].append(f'文件 {indexed_path} 的 serial 不匹配: 索引中为 {serial}, 文件中为 {file_serial}')
                            # 更新为正确的 serial
                            to_update[file_serial] = indexed_path
                            to_remove.append(serial)
                    else:
                        # 文件没有 front matter，需要添加
                        stats['errors'].append(f'文件 {indexed_path} 缺少 front matter')
            except Exception as e:
                stats['errors'].append(f'读取文件 {indexed_path} 失败: {e}')
        else:
            # 文件不存在，尝试在工作空间中搜索
            write_log(f'文件不存在: {indexed_path}，serial: {serial}，正在搜索...')
            found_path = find_file_by_serial(workspace_path, serial)

            if found_path:
                # 找到文件，更新索引
                new_relative_path = calculate_file_relative_path(workspace_path, found_path)
                to_update[serial] = new_relative_path
                stats['fixed'] += 1
                write_log(f'  找到文件，更新索引: {indexed_path} -> {new_relative_path}')

                # 如果 auto_fix，同时更新文件的 typora-root-url
                if auto_fix:
                    try:
                        add_front_matter_to_file(found_path, workspace_path)
                        write_log(f'  已更新文件 front matter')
                    except Exception as e:
                        stats['errors'].append(f'更新文件 front matter 失败: {e}')
            else:
                # 找不到文件，从索引中移除
                to_remove.append(serial)
                stats['removed'] += 1
                write_log(f'  文件已删除，从索引中移除: serial={serial}')

    # 应用更新
    if to_update or to_remove:
        for serial in to_remove:
            if serial in index_data:
                del index_data[serial]

        for serial, new_path in to_update.items():
            index_data[serial] = new_path

        write_index_file(index_path, index_data)
        write_log(f'索引验证完成: 已验证 {stats["verified"]} 个, 修复 {stats["fixed"]} 个, 移除 {stats["removed"]} 个')

        if stats['errors']:
            write_log(f'发现 {len(stats["errors"])} 个错误')
    else:
        write_log(f'索引验证完成: 所有 {stats["verified"]} 个文件均正常')

    return stats


def find_file_by_serial(workspace_path: str, serial: str) -> Optional[str]:
    """
    在工作空间中查找包含指定 serial 的 Markdown 文件

    Args:
        workspace_path: 工作空间路径
        serial: 要查找的 serial

    Returns:
        找到的文件绝对路径，未找到返回 None
    """
    # 搜索所有 .md 文件
    md_files = find_files_by_extension(workspace_path, 'md')

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                front_matter = get_existing_front_matter(content)
                if front_matter:
                    file_serial = extract_serial_from_front_matter(front_matter[0])
                    if file_serial == serial:
                        return md_file
        except Exception:
            continue

    return None


def add_front_matter_to_file(file_path: str, workspace_path: str) -> bool:
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

    relative_path = calculate_relative_path(workspace_path, file_path)

    if has_front_matter(content):
        # 有 front matter，解析并保留所有字段
        existing = get_existing_front_matter(content)
        if not existing:
            return False

        front_matter, remaining = existing
        fields = parse_front_matter(front_matter)
        existing_serial = extract_serial_from_front_matter(front_matter)
        existing_url = fields.get('typora-root-url')
        existing_copy_url = fields.get('typora-copy-images-to')

        # 计算新的 typora-root-url 和 typora-copy-images-to
        if existing_serial:
            # 使用现有的 serial 计算新的值
            new_typora_root_url = relative_path
            url_prefix = existing_serial[:2]
            if relative_path:
                new_typora_copy_images_to = f'{relative_path}.assets/{url_prefix}/{existing_serial}'
            else:
                new_typora_copy_images_to = f'.assets/{url_prefix}/{existing_serial}'

            # 检查是否需要更新 front matter
            if existing_url == new_typora_root_url and existing_copy_url == new_typora_copy_images_to:
                # front matter 无需更新，但要确保文件在索引中
                write_log(f'  front matter 无需更新，检查索引...')
                update_index(workspace_path, existing_serial, file_path)
                return False

            # 更新 typora-root-url 和 typora-copy-images-to，保留所有其他字段
            fields['typora-root-url'] = new_typora_root_url
            fields['typora-copy-images-to'] = new_typora_copy_images_to
            new_front_matter = build_front_matter(fields)

            new_content = new_front_matter + '\n\n' + remaining

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # 更新索引
            update_index(workspace_path, existing_serial, file_path)

            write_log(f'  更新 typora-root-url 和 typora-copy-images-to: serial={existing_serial}')
            return True
        else:
            # 没有 serial，生成新的，保留所有其他字段
            serial = generate_unique_serial(workspace_path)
            fields['serial'] = serial

            # 计算 typora-root-url 和 typora-copy-images-to
            typora_root_url = relative_path
            url_prefix = serial[:2]
            if relative_path:
                typora_copy_images_to = f'{relative_path}.assets/{url_prefix}/{serial}'
            else:
                typora_copy_images_to = f'.assets/{url_prefix}/{serial}'
            fields['typora-root-url'] = typora_root_url
            fields['typora-copy-images-to'] = typora_copy_images_to

            new_front_matter = build_front_matter(fields)
            new_content = new_front_matter + '\n\n' + remaining

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # 更新索引
            update_index(workspace_path, serial, file_path)

            write_log(f'  添加 serial、typora-root-url 和 typora-copy-images-to: serial={serial} (保留其他字段)')
            return True
    else:
        # 没有 front matter，添加新的
        serial = generate_unique_serial(workspace_path)
        new_front_matter = create_front_matter(serial, relative_path)

        new_content = new_front_matter + '\n\n' + content

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # 更新索引
        update_index(workspace_path, serial, file_path)

        write_log(f'  添加 front matter: serial={serial}')
        return True


def collect_markdown_files(paths: list[str], workspace_path: str) -> list[str]:
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
            found = find_files_by_extension(abs_path, 'md')
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
        nargs='+',
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

    # 收集所有需要处理的 markdown 文件
    md_files = collect_markdown_files(args.paths, workspace)

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
            relative_path = calculate_relative_path(workspace, md_file)
            write_log(f'处理: {relative_path}')
        except ValueError:
            # 文件不在工作空间内，显示绝对路径
            write_log(f'处理: {md_file} (警告: 文件不在工作空间内)')

        try:
            modified = add_front_matter_to_file(md_file, workspace)
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


if __name__ == '__main__':
    main()
