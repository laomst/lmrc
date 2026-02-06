#!/bin/zsh
# Zsh 环境配置入口文件
# 在 ~/.zshrc 中添加: source ~/__profile_workspace__/_bash_/zsh/index.zsh

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd)"

# 首先加载 exports.zsh（用于定义环境变量，如果存在的话）
[[ -r "$SCRIPT_DIR/exports.zsh" ]] && source "$SCRIPT_DIR/exports.zsh"

# 加载顺序：path -> function -> alias -> completion -> prompt
CONFIG_FILES=(
  "path.zsh"
  "function.zsh"
  "alias.zsh"
  "completion.zsh"
  "prompt.zsh"
  "claude.zsh"
)

# 已在 CONFIG_FILES 中的文件名（用于去重）
loaded_files=()
for config_file in "${CONFIG_FILES[@]}"; do
  file_path="$SCRIPT_DIR/$config_file"
  if [[ -r "$file_path" ]]; then
    source "$file_path"
    loaded_files+=("$config_file")
  else
    echo "[Warning] Cannot load config: $file_path" >&2
  fi
done

# 加载目录下其他配置文件（排除已加载的、exports.zsh 和 index.zsh 自己）
{
  setopt LOCAL_OPTIONS NULL_GLOB
  for config_file in "$SCRIPT_DIR"/*.zsh; do
    filename="${config_file:t}"
    # 跳过 exports.zsh、index.zsh 和已加载的文件
    if [[ "$filename" != "index.zsh" ]] && [[ "$filename" != "exports.zsh" ]] && [[ ! "${loaded_files[@]}" =~ "${filename}" ]]; then
      source "$config_file"
    fi
  done
}

unset SCRIPT_DIR CONFIG_FILES loaded_files config_file file_path filename
