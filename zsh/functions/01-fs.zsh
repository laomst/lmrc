# 文件系统操作

# 创建目录并进入
mkcd() {
  mkdir -p "$1" && cd "$1"
}

# 快速回退目录
back() {
  local count=${1:-1}
  local path=""
  repeat $count do
    path="../$path"
  done
  cd "$path"
}

# 查找并显示文件大小（按大小排序）
duf() {
  du -sh "$@" 2>/dev/null | sort -rh
}

# 显示当前目录最大的文件/目录
largest() {
  du -h . 2>/dev/null | sort -rh | head -n "${1:-10}"
}
