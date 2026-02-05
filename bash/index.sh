#!/bin/bash
# Bash 环境配置入口文件
# 在 ~/.bashrc 或 ~/.bash_profile 中添加: source ~/path/to/bash/index.sh

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 首先加载 exports.sh（用于定义环境变量，如果存在的话）
[[ -r "$SCRIPT_DIR/exports.sh" ]] && source "$SCRIPT_DIR/exports.sh"

# 加载顺序：path -> function -> alias -> completion -> prompt
CONFIG_FILES=(
  "path.sh"
  "function.sh"
  "alias.sh"
  "completion.sh"
  "prompt.sh"
)

# 统计加载结果
_loaded_count=0
_failed_count=0
declare -a loaded_files=()

for config_file in "${CONFIG_FILES[@]}"; do
  file_path="$SCRIPT_DIR/$config_file"
  if [[ -r "$file_path" ]]; then
    source "$file_path" && ((_loaded_count++)) || ((_failed_count++))
    loaded_files+=("$config_file")
  else
    echo "[Warning] Config file not found or not readable: $file_path" >&2
    ((_failed_count++))
  fi
done

# 加载目录下其他配置文件（排除已加载的和 index.sh 自己）
for config_file in "$SCRIPT_DIR"/*.sh; do
  [[ -e "$config_file" ]] || continue  # 处理无匹配文件的情况
  filename=$(basename "$config_file")
  # 跳过 index.sh 和已加载的文件
  if [[ "$filename" != "index.sh" ]] && [[ ! " ${loaded_files[@]} " =~ " ${filename} " ]]; then
    source "$config_file" && ((_loaded_count++)) || ((_failed_count++))
  fi
done

# 加载完成时显示简要信息（仅在交互式shell中）
if [[ $- == *i* ]]; then
  [[ $_loaded_count -gt 0 ]] && echo "Bash config loaded: $_loaded_count file(s)"
  [[ $_failed_count -gt 0 ]] && echo "Warning: $_failed_count file(s) failed to load" >&2
fi

unset SCRIPT_DIR CONFIG_FILES config_file file_path _loaded_count _failed_count
