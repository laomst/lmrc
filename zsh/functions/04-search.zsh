# 搜索操作

# 递归搜索文件内容
fif() {
  grep -r "$1" . --exclude-dir=".git" --exclude-dir="node_modules" \
    --exclude-dir="__pycache__" --color=always 2>/dev/null
}

# 搜索文件名
fn() {
  find . -name "*$1*" 2>/dev/null
}
