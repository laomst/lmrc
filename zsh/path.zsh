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
# 正序遍历数组，依次拼接有效路径，然后整体添加到 PATH 前面
# 不检查 PATH 中是否已存在，直接将声明的路径优先级提至最高
local new_paths=""
for path_entry in "${CUSTOM_PATHS[@]}"; do
  if [[ -d "$path_entry" ]]; then
    if [[ -n "$new_paths" ]]; then
      new_paths="$new_paths:$path_entry"
    else
      new_paths="$path_entry"
    fi
  fi
done

# 导出自定义路径环境变量
if [[ -n "$new_paths" ]]; then
  export LMRC_PATH="$new_paths"
  PATH="$LMRC_PATH:$PATH"
fi

export PATH
