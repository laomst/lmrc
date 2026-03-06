#!/bin/zsh
# 自动补全配置

# 启用补全系统
autoload -Uz compinit && compinit

# 补全选项
setopt COMPLETE_IN_WORD       # 在单词中间也能补全
setopt AUTO_LIST              # 自动列出选项
setopt AUTO_MENU              # 自动使用菜单
setopt MENU_COMPLETE          # 自动选择第一个匹配项

# 补全样式
zstyle ':completion:*' menu select                    # 菜单选择模式
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS} # 彩色显示
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'   # 大小写不敏感
zstyle ':completion:*' verbose yes                    # 详细显示
zstyle ':completion:*:descriptions' format '%B%d%b'   # 描述格式
zstyle ':completion:*:warnings' format '%F{red}No matches%f'

# 缓存补全结果
zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path "$HOME/.zcompcache"

# 补全组排序
zstyle ':completion:*:*:*:*:*' menu select
zstyle ':completion:::::' completer _expand _complete _ignored _approximate

# kill 命令补全（只补全当前用户的进程）
zstyle ':completion:*:*:kill:*' command 'ps -u $USER -o pid,%cpu,tty,cputime,cmd'
zstyle ':completion:*:*:kill:*' insert-identical
zstyle ':completion:*:*:kill:*' menu yes select
zstyle ':completion:*:*:kill:*' force-list always
zstyle ':completion:*:*:kill:*' kill-pre-commands ps
