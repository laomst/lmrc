# 环境变量配置

# ============================================
# SDK 路径配置
# ============================================

# 定义 SDK 根目录
$env:SDK_HOME_DIR = "C:\SDK"

# JAVA 配置
$env:JAVA8_HOME = "$env:SDK_HOME_DIR\Java\jdk-1.8"
$env:JAVA21_HOME = "$env:SDK_HOME_DIR\Java\jdk-21"
$env:JAVA_HOME = $env:JAVA21_HOME

# Maven 配置
$env:MAVEN_HOME = "$env:SDK_HOME_DIR\apache-maven-3.6.3"

# Python 配置（通常由安装程序自动设置，按需取消注释）
# $env:PYTHON_HOME = "C:\Python313"
