#!/bin/zsh
# 提示符配置

# 加载 vcs_info 模块
autoload -Uz vcs_info
autoload -Uz colors && colors

# 配置 vcs_info
zstyle ':vcs_info:*' enable git
zstyle ':vcs_info:*' check-for-changes true
zstyle ':vcs_info:*' stagedstr "%F{yellow}*%f"
zstyle ':vcs_info:*' unstagedstr "%F{red}+%f"
zstyle ':vcs_info:git:*' formats ' [%b%u%c]'
zstyle ':vcs_info:git:*' actionformats ' [%b|%a%u%c]'

# 预执行函数，获取 git 信息
precmd() {
  vcs_info
}

# 设置提示符
setopt PROMPT_SUBST

# 主提示符：时间 用户@主机:路径 (git分支) $
PROMPT='%B%F{blue}[%*]%f %F{green}%n%f@%F{yellow}%m%f:%B%F{cyan}%c%f${vcs_info_msg_0_} %(?.%F{green}.%F{red})$%%%f '

# 右侧提示符（显示完整路径）
RPROMPT='%F{blue}%~%f'

# PS2 (多行命令续行)
PS2='%F{yellow}>%f '

# PS3 (select 菜单)
PS3='%F{cyan}#%f '

# PS4 (调试模式)
PS4='%F{blue}+%f '
