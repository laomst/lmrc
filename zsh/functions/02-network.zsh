# 网络操作

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
  if timeout 3 zsh -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; then
    echo "Port $port is open"
  else
    echo "Port $port is closed"
  fi
}
