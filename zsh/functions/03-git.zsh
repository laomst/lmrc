# Git 操作

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
