import os


def find_files_by_extension(directory, extension):
    file_list = []
    # 遍历目录
    for entry in os.scandir(directory):
        # 如果是文件且扩展名匹配
        if entry.is_file() and entry.name.endswith(f'.{extension}'):
            file_list.append(entry.path)
        # 如果是目录，递归查找
        elif entry.is_dir():
            file_list.extend(find_files_by_extension(entry.path, extension))

    return file_list