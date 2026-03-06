#!/bin/zsh
# 放置一份公共的需要 export 的环境变量

# ============================================
# SDK 路径配置
# ============================================

# 定义 SDK 根目录
export SDK_HOME_DIR="/Library"

# JAVA 配置
export JAVA8_HOME="$SDK_HOME_DIR/Java/JavaVirtualMachines/jdk-1.8.jdk/Contents/Home"
export JAVA21_HOME="$SDK_HOME_DIR/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home"
export JAVA_HOME="$JAVA21_HOME"

# Maven 配置
export MAVEN_HOME="$SDK_HOME_DIR/apache-maven-3.6.3"

# Python 配置
export PYTHON_HOME="/Library/Frameworks/Python.framework/Versions/3.13"
