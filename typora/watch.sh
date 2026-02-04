#!/bin/bash
# Typora 工作空间文件监控服务启动脚本
# 自动激活虚拟环境并运行 Python 脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# 检查虚拟环境是否存在
if [[ ! -d "$VENV_DIR" ]]; then
  echo "[Error] Virtual environment not found at: $VENV_DIR"
  echo "Please create it first:"
  echo "  cd $SCRIPT_DIR"
  echo "  python3 -m venv venv"
  echo "  source venv/bin/activate"
  echo "  pip install -r scripts/requirements.txt"
  exit 1
fi

# 激活虚拟环境并运行脚本
source "$VENV_DIR/bin/activate"
python "$SCRIPT_DIR/scripts/watch_workspace.py" "$@"
deactivate
