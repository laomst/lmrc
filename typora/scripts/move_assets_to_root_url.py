#!/usr/bin/env python3
"""
将markdown文件assets目录中的图片移动到typora-root-url指定的目录中

工作空间配置：
    通过以下两种方式之一指定工作空间路径（优先级从高到低）：
    1. 命令行参数: -w /path/to/workspace
    2. 环境变量: export TYPORA_WORKSPACE=/path/to/workspace

使用方式:
    # 使用环境变量配置的工作空间
    python move_assets_to_root_url.py

    # 指定工作空间路径
    python move_assets_to_root_url.py -w /path/to/workspace
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

from util.logger import write_log

# 环境变量名称
TYPORA_WORKSPACE_ENV = 'TYPORA_WORKSPACE'


def parse_front_matter(markdown_file: Path) -> dict:
    """
    解析markdown文件的front matter，返回包含typora-root-url等字段的字典

    Args:
        markdown_file: markdown文件路径

    Returns:
        包含front matter字段的字典
    """
    front_matter = {}

    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 匹配 --- 包围的front matter
        pattern = r'^---\s*\n(.*?)\n---'
        match = re.match(pattern, content, re.DOTALL)

        if match:
            fm_content = match.group(1)
            for line in fm_content.split('\n'):
                # 匹配 key: value 格式
                kv_match = re.match(r'^\s*([a-zA-Z0-9_-]+):\s*(.*?)\s*$', line)
                if kv_match:
                    key = kv_match.group(1)
                    value = kv_match.group(2)
                    front_matter[key] = value
    except Exception as e:
        write_log(f"解析front matter失败: {markdown_file}, 错误: {e}")

    return front_matter


def get_asset_images(asset_dir: Path) -> list[Path]:
    """
    获取assets目录下的所有图片文件

    Args:
        asset_dir: assets目录路径

    Returns:
        图片文件路径列表
    """
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico'}
    images = []

    if asset_dir.exists() and asset_dir.is_dir():
        for file in asset_dir.iterdir():
            if file.is_file() and file.suffix.lower() in image_extensions:
                images.append(file)

    return images


def update_markdown_image_links(markdown_file: Path, file_stem: str, serial: str, dry_run: bool = False) -> int:
    """
    更新markdown文件中的图片链接，将.assets/文件名/替换为/.assets/{serial前两位}/{serial}/

    使用简单的字符串替换，避免正则表达式的转义问题

    Args:
        markdown_file: markdown文件路径
        file_stem: markdown文件名(不含扩展名)
        serial: 文章的 serial
        dry_run: 是否仅模拟运行

    Returns:
        替换的链接数量
    """
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        write_log(f"  读取文件失败: {e}")
        return 0

    # 构建新的图片路径: /.assets/{serial前两位}/{serial}/
    new_path = f'/.assets/{serial[:2]}/{serial}/'

    # 需要替换的旧路径
    old_path_1 = f'.assets/{file_stem}/'
    old_path_2 = f'./.assets/{file_stem}/'

    # 统计替换次数
    count_1 = content.count(old_path_1)
    count_2 = content.count(old_path_2)

    # 执行替换
    content = content.replace(old_path_1, new_path)
    content = content.replace(old_path_2, new_path)

    replaced_count = count_1 + count_2

    if replaced_count > 0:
        if not dry_run:
            try:
                with open(markdown_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                write_log(f"  更新链接: {replaced_count} 个")
            except Exception as e:
                write_log(f"  写入文件失败: {e}")
                return 0
        else:
            write_log(f"  [模拟] 更新链接: {replaced_count} 个")
    else:
        # 检查是否有类似的路径但未被替换
        if '.assets/' in content and file_stem in content:
            write_log(f"  警告: 文件中包含.assets和{file_stem}，但未找到匹配的图片路径")

    return replaced_count


def move_images_to_root_url(markdown_file: Path, dry_run: bool = False) -> int:
    """
    将markdown文件assets目录中的图片移动到typora-copy-images-to指定的目录

    Args:
        markdown_file: markdown文件路径
        dry_run: 是否仅模拟运行，不实际移动文件

    Returns:
        成功移动的图片数量
    """
    # 获取markdown文件名(不含扩展名)
    file_stem = markdown_file.stem

    # 解析front matter获取typora-copy-images-to和serial
    front_matter = parse_front_matter(markdown_file)
    copy_images_to = front_matter.get('typora-copy-images-to')
    serial = front_matter.get('serial')

    if not copy_images_to:
        write_log(f"跳过 (无typora-copy-images-to): {markdown_file}")
        return 0

    if not serial:
        write_log(f"跳过 (无serial): {markdown_file}")
        return 0

    # 构建源目录路径: ./.assets/文件名/
    asset_dir = markdown_file.parent / '.assets' / file_stem

    # 获取所有图片
    images = get_asset_images(asset_dir)

    if not images:
        write_log(f"跳过 (无图片): {markdown_file}")
        return 0

    # 构建目标目录 (基于markdown文件的相对路径)
    # typora-copy-images-to是相对于markdown文件的路径
    target_dir = markdown_file.parent / copy_images_to

    # 创建目标目录(如果不存在)
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        write_log(f"  [模拟] 创建目录: {target_dir}")

    moved_count = 0

    # 移动图片
    for img in images:
        target_path = target_dir / img.name

        # 如果目标文件已存在，添加后缀
        if target_path.exists():
            base = target_path.stem
            ext = target_path.suffix
            counter = 1
            while target_path.exists():
                target_path = target_dir / f"{base}_{counter}{ext}"
                counter += 1

        if dry_run:
            write_log(f"  [模拟] 移动: {img} -> {target_path}")
        else:
            try:
                shutil.move(str(img), str(target_path))
                write_log(f"  移动: {img.name} -> {target_path}")
                moved_count += 1
            except Exception as e:
                write_log(f"  移动失败: {img}, 错误: {e}")

    # 检查并清理空的assets目录
    if not dry_run:
        asset_parent = asset_dir.parent
        if asset_dir.exists() and not list(asset_dir.iterdir()):
            asset_dir.rmdir()
            write_log(f"  清理空目录: {asset_dir}")

        if asset_parent.exists() and not list(asset_parent.iterdir()):
            asset_parent.rmdir()
            write_log(f"  清理空目录: {asset_parent}")

    # 更新markdown文件中的图片链接
    if moved_count > 0:
        update_markdown_image_links(markdown_file, file_stem, serial, dry_run=dry_run)

    return moved_count


def walk_markdown_files(root_dir: Path) -> list[Path]:
    """
    遍历目录，返回所有markdown文件

    Args:
        root_dir: 根目录

    Returns:
        markdown文件路径列表
    """
    markdown_extensions = {'.md', '.markdown', '.mdown', '.mkd'}
    markdown_files = []

    for file in root_dir.rglob('*'):
        if file.is_file() and file.suffix.lower() in markdown_extensions:
            markdown_files.append(file)

    return sorted(markdown_files)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将 Markdown 文件 assets 目录中的图片移动到 typora-root-url 指定的目录',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  %(prog)s                                   # 使用环境变量配置的工作空间
  %(prog)s -w /workspace                     # 指定工作空间路径
  %(prog)s --dry-run                         # 模拟运行（不实际移动文件）
        '''
    )

    parser.add_argument(
        '-w', '--workspace',
        default=None,
        help='工作空间路径（也可通过环境变量 TYPORA_WORKSPACE 设置）'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='模拟运行模式，不实际移动文件'
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

    workspace_root = Path(workspace).resolve()

    if not workspace_root.exists():
        write_log(f"错误: 目标目录不存在: {workspace_root}")
        sys.exit(1)

    # 显示配置信息
    write_log("=" * 60)
    write_log("图片迁移工具")
    write_log("=" * 60)
    write_log(f"工作空间: {workspace_root}")
    write_log("")

    if args.dry_run:
        write_log("[模拟模式] 不会实际移动文件")
    else:
        write_log("[实际模式] 将实际移动文件!")
        response = input("确认继续? [y/N]: ").strip().lower()
        if response not in ('y', 'yes'):
            write_log("取消操作")
            sys.exit(0)

    write_log("")
    write_log("开始处理...")
    write_log("-" * 60)

    # 遍历所有markdown文件
    markdown_files = walk_markdown_files(workspace_root)
    write_log(f"找到 {len(markdown_files)} 个markdown文件")
    write_log("")

    total_moved = 0
    processed = 0

    for md_file in markdown_files:
        moved = move_images_to_root_url(md_file, dry_run=args.dry_run)
        if moved > 0:
            total_moved += moved
            processed += 1

    write_log("-" * 60)
    write_log("")
    write_log(f"处理完成:")
    write_log(f"  处理文件数: {processed}")
    write_log(f"  移动图片数: {total_moved}")

    if args.dry_run:
        write_log("")
        write_log("[注意] 这是模拟运行，没有实际移动文件")


if __name__ == '__main__':
    main()
