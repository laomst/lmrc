#!/bin/bash
# 命令别名配置

# ls 别名
alias lsa="ls -a"
alias ll="ls -alF"
alias la="ls -A"
alias l="ls -CF"

# 路径查看
alias pathls='echo "${PATH//:/\n}"'

# Python 别名（仅当 python3 存在但 python 不存在时设置）
if command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
  alias python='python3'
fi
if command -v pip3 &>/dev/null && ! command -v pip &>/dev/null; then
  alias pip='pip3'
fi

# 常用快捷方式
alias ..='cd ..'
alias ...='cd ../..'
alias home='cd ~'

# Git 别名
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
