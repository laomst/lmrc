#!/bin/bash
# PATH 环境变量配置

# 定义 SDK 根目录
SDK_HOME_DIR="/Library"

# JAVA 配置（仅当路径存在时设置）
_JAVA8_PATH="$SDK_HOME_DIR/Java/JavaVirtualMachines/jdk-1.8.jdk/Contents/Home"
_JAVA21_PATH="$SDK_HOME_DIR/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home"

if [[ -d "$_JAVA21_PATH" ]]; then
  export JAVA_HOME="$_JAVA21_PATH"
elif [[ -d "$_JAVA8_PATH" ]]; then
  export JAVA_HOME="$_JAVA8_PATH"
fi

# Maven 配置（仅当路径存在时设置）
_MAVEN_PATH="$SDK_HOME_DIR/apache-maven-3.6.3"
[[ -d "$_MAVEN_PATH" ]] && export MAVEN_HOME="$_MAVEN_PATH"

# Python 配置（仅当路径存在时设置）
_PYTHON_PATH="/Library/Frameworks/Python.framework/Versions/3.13"
[[ -d "$_PYTHON_PATH" ]] && export PYTHON_HOME="$_PYTHON_PATH"

# 自定义路径（按优先级排序）
CUSTOM_PATHS=(
  "${MAVEN_HOME:+$MAVEN_HOME/bin}"
  "${JAVA_HOME:+$JAVA_HOME/bin}"
  "${PYTHON_HOME:+$PYTHON_HOME/bin}"
  "/opt/homebrew/bin"
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
unset _JAVA8_PATH _JAVA21_PATH _MAVEN_PATH _PYTHON_PATH _path_add_to_front
