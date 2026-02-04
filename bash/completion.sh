#!/bin/bash
# 自动补全配置

# 加载系统补全
[[ -f /etc/bash_completion ]] && source /etc/bash_completion
[[ -f /usr/local/etc/bash_completion ]] && source /usr/local/etc/bash_completion
[[ -f /opt/homebrew/etc/bash_completion ]] && source /opt/homebrew/etc/bash_completion

# cd 命令只补全目录
complete -d cd

# man 命令补全
complete -c man

# kill/killall 补全进程名
complete -c kill killall

# SSH/SCP/SFTP/Rsync 从 known_hosts 和 ssh config 补全
_ssh_hosts_completion() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local hosts=()

  # 从 known_hosts 读取
  local known_hosts_file="$HOME/.ssh/known_hosts"
  if [[ -f "$known_hosts_file" ]]; then
    while read -r line; do
      [[ -z "$line" || "$line" == \#* ]] && continue
      hosts+=("${line%%[ ,]*}")
    done < <(awk '{print $1}' "$known_hosts_file" 2>/dev/null)
  fi

  # 从 ssh config 读取
  local ssh_config="$HOME/.ssh/config"
  if [[ -f "$ssh_config" ]]; then
    while read -r host; do
      hosts+=("$host")
    done < <(awk '/^Host[[:space:]]/ {print $2}' "$ssh_config" 2>/dev/null)
  fi

  # 去重并生成补全
  local unique_hosts=($(printf "%s\n" "${hosts[@]}" | sort -u))
  COMPREPLY=($(compgen -W "${unique_hosts[*]}" -- "$cur"))
}

complete -F _ssh_hosts_completion ssh scp sftp rsync

# Git 补全
if [[ -f ~/.git-completion.bash ]]; then
  source ~/.git-completion.bash
fi

# make 补全（包含 Makefile 中的目标）
complete -f -X "!*.?[mh]" make
