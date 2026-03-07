#!/bin/zsh
# 公共工具函数

# 检测环境变量是否存在值
# 用法: check-env-exists "JAVA_HOME" "GOPATH" "NODE_HOME"
# 所有变量都有值时返回 0，否则打印缺失的变量名并返回 1
check-env-exists() {
  local missing=()
  for name in "$@"; do
    if [[ -z "${(P)name}" ]]; then
      missing+=("$name")
    fi
  done

  if [[ ${#missing[@]} -eq 0 ]]; then
    return 0
  fi

  for name in "${missing[@]}"; do
    printf '\033[1;31m环境变量未设置: %s\033[0m\n' "$name"
  done
  return 1
}
