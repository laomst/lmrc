# 进程操作

# 按名称查找进程
psgrep() {
  ps aux | grep -i "$1" | grep -v grep
}

# 按名称杀死进程
pskill() {
  local pid
  pid=$(psgrep "$1" | awk '{print $2}' | head -n 1)
  if [[ -n "$pid" ]]; then
    kill "$pid"
    echo "Killed process $pid"
  else
    echo "No process found matching: $1"
  fi
}
