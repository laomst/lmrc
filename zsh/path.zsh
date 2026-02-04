#!/bin/zsh
# PATH 环境变量配置

# 定义 SDK 根目录
SDK_HOME_DIR="/Library"

# JAVA 配置
export JAVA8_HOME="$SDK_HOME_DIR/Java/JavaVirtualMachines/jdk-1.8.jdk/Contents/Home"
export JAVA21_HOME="$SDK_HOME_DIR/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home"
export JAVA_HOME="$JAVA21_HOME"

# Maven 配置
export MAVEN_HOME="$SDK_HOME_DIR/apache-maven-3.6.3"

# Python 配置
export PYTHON_HOME="/Library/Frameworks/Python.framework/Versions/3.13"

# 自定义路径（按优先级排序）
typeset -a CUSTOM_PATHS
CUSTOM_PATHS=(
  "$HOME/.local/bin"
  "$MAVEN_HOME/bin"
  "$JAVA_HOME/bin"
  "$PYTHON_HOME/bin"
  "/opt/homebrew/bin"
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
