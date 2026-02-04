#!/bin/zsh
# PATH 环境变量配置
#
# 机器相关的环境变量（SDK_HOME_DIR、JAVA_HOME、MAVEN_HOME、PYTHON_HOME 等）
# 应在 exports.zsh 中定义，此处使用默认值作为后备

# 默认 SDK 根目录（可通过 exports.zsh 覆盖）
: ${SDK_HOME_DIR:=/Library}

# 自定义路径（按优先级排序）
typeset -a CUSTOM_PATHS
CUSTOM_PATHS=(
  "$HOME/.local/bin"
  "${MAVEN_HOME:+$MAVEN_HOME/bin}"
  "${JAVA_HOME:+$JAVA_HOME/bin}"
  "${PYTHON_HOME:+$PYTHON_HOME/bin}"
  "${HOMEBREW_PREFIX:-/opt/homebrew}/bin"
)

# 将自定义路径添加到 PATH 前面（数组靠前的元素优先级更高）
# 反向遍历数组，先处理后面的元素，最后处理前面的元素（放到最前面）
for ((i=${#CUSTOM_PATHS[@]}-1; i>=0; i--)); do
  path_entry="${CUSTOM_PATHS[i]}"
  if [[ -d "$path_entry" ]] && [[ ":$PATH:" != *":$path_entry:"* ]]; then
    PATH="$path_entry:$PATH"
  fi
done

export PATH
