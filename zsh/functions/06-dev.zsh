# 开发工具

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
  if command -v jq &>/dev/null; then
    jq '.' "$1"
  elif command -v python3 &>/dev/null; then
    python3 -m json.tool "$1"
  else
    echo "Neither jq nor python3 found"
    return 1
  fi
}
