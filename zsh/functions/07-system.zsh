# 系统信息与工具

# 显示磁盘使用情况
diskusage() {
  df -h | grep -E "Filesystem|/dev/"
}

# 显示内存使用情况
memusage() {
  if [[ "$OSTYPE" == darwin* ]]; then
    vm_stat | perl -ne '/page size of (\d+)/ and $ps=$1; /Pages\s+(.+):\s+(\d+)/ and printf("%-16s % 16s MB\n", "$1:", $2*$ps/1048576);'
  else
    free -h
  fi
}

# 显示 PATH 列表
# 选项:
#   -i, --info    分块显示 LMRC_PATH 和 PATH 的详细内容
pathls() {
  local show_info=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -i|--info)
        show_info=true
        shift
        ;;
      *)
        echo "Usage: pathls [-i|--info]" >&2
        return 1
        ;;
    esac
  done

  if [[ "$show_info" == true ]]; then
    echo "\033[1;34m=== LMRC_PATH ===\033[0m"
    if [[ -n "$LMRC_PATH" ]]; then
      echo ${(j:\n:)${(@s/:/)LMRC_PATH}}
    else
      echo "(empty)"
    fi

    echo "\n\033[1;34m=== PATH ===\033[0m"
    echo ${(j:\n:)${(@s/:/)PATH}}
  else
    echo ${(j:\n:)${(@s/:/)PATH}}
  fi
}

# 显示 256 色测试
colors256() {
  for c in {0..255}; do
    printf "\033[38;5;%cm %3s \033[0m" "$c" "$c"
    ((c % 16 == 15)) && echo
  done
}

# 搜索命令历史
histgrep() {
  history | grep -i "$1"
}

# 秒表（Ctrl+C 停止）
stopwatch() {
  local begin_date=$(date +%s)
  while true; do
    local now=$(date +%s)
    local elapsed=$((now - begin_date))
    local minutes=$((elapsed / 60))
    local seconds=$((elapsed % 60))
    printf "\r%02d:%02d" "$minutes" "$seconds"
    sleep 1
  done
}
