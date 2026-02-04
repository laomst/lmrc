#!/bin/bash
# 提示符配置

# 获取 Git 分支和状态
_git_prompt() {
  # 快速检查是否在git仓库中
  git rev-parse --git-dir &>/dev/null || return

  local branch
  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || return

  local status=""
  local status_output

  # 使用 git status --porcelain 获取状态（一次调用获取所有信息）
  status_output=$(git status --porcelain 2>/dev/null)

  if [[ -n "$status_output" ]]; then
    # 检查是否有任何修改（暂存或未暂存）
    # git status --porcelain 格式: XY 文件名
    # X=暂存区状态, Y=工作目录状态, 空格表示无变化
    while IFS= read -r line; do
      # 跳过空行
      [[ -z "$line" ]] && continue

      local staged="${line:0:1}"
      local unstaged="${line:1:1}"

      # 检查是否有修改（暂存区或工作目录）
      if [[ "$staged" != " " ]] || [[ "$unstaged" != " " ]]; then
        status="${status}*"
      fi

      # 检查是否有未跟踪文件
      if [[ "$staged" == "?" ]]; then
        status="${status}+"
      fi

      # 如果已找到所有标记就提前退出
      [[ "$status" == "*+" ]] && break
    done <<< "$status_output"
  fi

  echo " [$branch$status]"
}

# 动态生成提示符
__prompt_command() {
  local exit_code=$?
  local git_info
  git_info=$(_git_prompt)

  # 根据上一条命令的退出码改变颜色
  local prompt_char="\[\033[32m\]\$"  # green
  ((exit_code != 0)) && prompt_char="\[\033[31m\]\$"  # red

  PS1="\[\033[1;34m\][\t]\[\033[0m\] "                    # time
  PS1+="\[\033[32m\]\u\[\033[0m\]@"                      # user
  PS1+="\[\033[33m\]\h\[\033[0m\]:"                      # host
  PS1+="\[\033[1;36m\]\W\[\033[0m\]"                     # path
  PS1+="\[\033[35m\]${git_info}\[\033[0m\] "             # git
  PS1+="${prompt_char}\[\033[0m\] "                      # prompt char
}

PROMPT_COMMAND="__prompt_command"

# PS2 (多行命令续行)
PS2="\[\033[33m\]>\[\033[0m\] "

# PS3 (select 菜单)
PS3="\[\033[36m\]#\[\033[0m\] "

# PS4 (调试模式)
PS4="\[\033[34m\]+\[\033[0m\] "
