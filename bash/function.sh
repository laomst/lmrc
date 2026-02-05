#!/bin/bash
# 自定义函数库

# ==================== 文件系统操作 ====================

# 创建目录并进入
mkcd() {
  if [[ -z "$1" ]]; then
    echo "Usage: mkcd <directory>" >&2
    return 1
  fi
  mkdir -p "$1" && cd "$1" || return 1
}

# 快速回退目录
back() {
  local count=${1:-1}
  # 验证参数是正整数
  if ! [[ "$count" =~ ^[0-9]+$ ]] || [[ "$count" -lt 1 ]]; then
    echo "Usage: back [count]" >&2
    return 1
  fi
  local path=""
  for ((i = 0; i < count; i++)); do
    path="../$path"
  done
  cd "$path" || return 1
}

# 查找并显示文件大小（按大小排序）
duf() {
  du -sh "$@" 2>/dev/null | sort -rh
}

# 显示当前目录最大的文件/目录
largest() {
  du -h . 2>/dev/null | sort -rh | head -n "${1:-10}"
}

# ==================== 网络操作 ====================

# 获取本机 IP 地址
myip() {
  if command -v ipconfig &>/dev/null; then
    ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null
  else
    hostname -I 2>/dev/null | awk '{print $1}'
  fi
}

# 获取公网 IP
publicip() {
  curl -s https://api.ipify.org
}

# 测试端口连通性
testport() {
  local host=$1 port=$2
  timeout 3 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null &&
    echo "Port $port is open" || echo "Port $port is closed"
}

# ==================== Git 操作 ====================

# Git 日志美化（单行）
gitlog() {
  git log --oneline --graph --decorate --all "$@"
}

# Git 查看分支图
gitgraph() {
  git log --graph --oneline --all --decorate "$@"
}

# 快速创建并切换到新分支
gbn() {
  git checkout -b "$1"
}

# ==================== 搜索操作 ====================

# 递归搜索文件内容
fif() {
  grep -r "$1" . --exclude-dir=".git" --exclude-dir="node_modules" \
    --exclude-dir="__pycache__" --color=always 2>/dev/null
}

# 搜索文件名
fn() {
  find . -name "*$1*" 2>/dev/null
}

# ==================== 进程操作 ====================

# 按名称查找进程
psgrep() {
  ps aux | grep -i "$1" | grep -v grep
}

# 按名称杀死进程
pskill() {
  if [[ -z "$1" ]]; then
    echo "Usage: pskill <pattern> [-9]" >&2
    return 1
  fi

  local force=0
  [[ "$2" == "-9" ]] && force=1

  local pid
  pid=$(psgrep "$1" | awk '{print $2}' | head -n 1)

  if [[ -n "$pid" ]]; then
    if [[ $force -eq 1 ]]; then
      kill -9 "$pid" && echo "Force killed process $pid"
    else
      kill "$pid" && echo "Killed process $pid"
    fi
  else
    echo "No process found matching: $1" >&2
    return 1
  fi
}

# ==================== 开发相关 ====================

# 快速启动 HTTP 服务器
server() {
  local port=${1:-8000}
  if command -v python3 &>/dev/null; then
    echo "Starting HTTP server on port $port..."
    python3 -m http.server "$port"
  elif command -v python &>/dev/null; then
    echo "Starting HTTP server on port $port..."
    python -m SimpleHTTPServer "$port"
  else
    echo "Python not found"
    return 1
  fi
}

# 显示 JSON 格式化
jsonfmt() {
  local tool=""
  if command -v jq &>/dev/null; then
    tool="jq"
  elif command -v python3 &>/dev/null; then
    tool="python3"
  else
    echo "Error: Neither jq nor python3 found" >&2
    return 1
  fi

  if [[ -n "$1" ]]; then
    # 从文件读取
    if [[ "$tool" == "jq" ]]; then
      jq '.' "$1"
    else
      python3 -m json.tool "$1"
    fi
  else
    # 从 stdin 读取
    if [[ "$tool" == "jq" ]]; then
      jq '.'
    else
      python3 -m json.tool
    fi
  fi
}

# ==================== 系统信息 ====================

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

# ==================== 历史命令 ====================

# 搜索命令历史
histgrep() {
  history | grep -i "$1"
}

# ==================== 压缩/解压 ====================

# 智能解压任意格式文件
extract() {
  if [[ -f "$1" ]]; then
    case "$1" in
      *.tar.bz2)   tar xjf "$1" ;;
      *.tar.gz)    tar xzf "$1" ;;
      *.bz2)       bunzip2 "$1" ;;
      *.rar)       unrar x "$1" ;;
      *.gz)        gunzip "$1" ;;
      *.tar)       tar xf "$1" ;;
      *.tbz2)      tar xjf "$1" ;;
      *.tgz)       tar xzf "$1" ;;
      *.zip)       unzip "$1" ;;
      *.Z)         uncompress "$1" ;;
      *.7z)        7z x "$1" ;;
      *)           echo "'$1' cannot be extracted via extract()" ;;
    esac
  else
    echo "'$1' is not a valid file"
  fi
}

# 创建 tar.gz 压缩包
targz() {
  tar -czf "${1}.tar.gz" "${1}"
}

# ==================== 时间相关 ====================

# 秒表（Ctrl+C 停止）
stopwatch() {
  local begin_date=$(date +%s)
  local trap_done=0

  # 优雅退出处理
  _stopwatch_cleanup() {
    [[ $trap_done -eq 1 ]] && return
    trap_done=1
    echo  # 换行
    return 0
  }

  trap '_stopwatch_cleanup' EXIT

  while true; do
    local now=$(date +%s)
    local elapsed=$((now - begin_date))
    local minutes=$((elapsed / 60))
    local seconds=$((elapsed % 60))
    printf "\r%02d:%02d" "$minutes" "$seconds"
    sleep 1
  done
}

# ==================== 颜色/主题 ====================

# ==================== 路径查看 ====================

# 显示 PATH 列表
# 选项:
#   -i, --info    分块显示 LMRC_PATH 和 PATH 的详细内容
pathls() {
  local show_info=false

  # 解析参数
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
    # 分块显示 LMRC_PATH 和 PATH
    echo "\033[1;34m=== LMRC_PATH ===\033[0m"
    if [[ -n "$LMRC_PATH" ]]; then
      echo "${LMRC_PATH//:/$'\n'}"
    else
      echo "(empty)"
    fi

    echo -e "\n\033[1;34m=== PATH ===\033[0m"
    echo "${PATH//:/$'\n'}"
  else
    # 默认显示完整 PATH
    echo "${PATH//:/$'\n'}"
  fi
}

# ==================== 颜色/主题 ====================

# 显示 256 色测试
colors256() {
  for c in {0..255}; do
    printf "\033[38;5;%cm %3s \033[0m" "$c" "$c"
    ((c % 16 == 15)) && echo
  done
}
