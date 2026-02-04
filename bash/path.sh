#!/bin/bash
# PATH 环境变量配置
#
# 机器相关的环境变量（SDK_HOME_DIR、JAVA_HOME、MAVEN_HOME、PYTHON_HOME 等）
# 应在 exports.sh 中定义，此处使用默认值作为后备

# 默认 SDK 根目录（可通过 exports.sh 覆盖）
: ${SDK_HOME_DIR:=/Library}

# 自定义路径（按优先级排序）
CUSTOM_PATHS=(
  "${MAVEN_HOME:+$MAVEN_HOME/bin}"
  "${JAVA_HOME:+$JAVA_HOME/bin}"
  "${PYTHON_HOME:+$PYTHON_HOME/bin}"
  "${HOMEBREW_PREFIX:-/opt/homebrew}/bin"
)

# 将自定义路径添加到 PATH 前面
_path_add_to_front() {
  local path_entry="$1"
  # 跳过空路径和已存在的路径
  [[ -z "$path_entry" ]] && return
  [[ -d "$path_entry" ]] || return
  [[ ":$PATH:" == *":$path_entry:"* ]] && return

  PATH="$path_entry:$PATH"
}

# 反向遍历数组，先处理后面的元素，最后处理前面的元素（放到最前面）
for ((i=${#CUSTOM_PATHS[@]}-1; i>=0; i--)); do
  _path_add_to_front "${CUSTOM_PATHS[i]}"
done

export PATH

# 清理临时变量
unset _path_add_to_front
