#!/bin/zsh
# 脚本加载工具函数
# 固定加载 includes.ini 配置文件

# ============================================
# 缓存：includes.ini 的 section 内容
# ============================================
typeset -gA _ini_cache=()
typeset -g _ini_loaded=false

# 解析 includes.ini 并缓存
_parse_ini() {
  [[ "$_ini_loaded" == true ]] && return 0
  _ini_loaded=true

  local config_file="$_LMRC_INCLUDES_INI" current_section="" line
  [[ ! -r "$config_file" ]] && return 1

  while IFS= read -r line || [[ -n "$line" ]]; do
    # 跳过空行和注释
    [[ -z "$line" || "$line" =~ '^[[:space:]]*#' ]] && continue

    # 检测 section
    if [[ "$line" =~ '^\[([^]]+)\]' ]]; then
      current_section="${match[1]}"
      _ini_cache[$current_section]=""
      continue
    fi

    # 追加路径到当前 section（仅支持绝对路径）
    if [[ -n "$current_section" && "$line" =~ '^/|^\~' ]]; then
      _ini_cache[$current_section]+="${_ini_cache[$current_section]:+$'\n'}$line"
    fi
  done < "$config_file"
}

# ============================================
# 公开函数
# ============================================

# 加载单个脚本
# 用法: load_script "path/to/script.zsh"
load_script() {
  [[ -z "$1" ]] && return 1
  local expanded="${(e)1}"
  # shellcheck disable=SC1090
  [[ -r "$expanded" ]] && source "$expanded"
}

# 加载指定 section 下的脚本
# 用法: load_section "section_name"
load_section() {
  _parse_ini
  local content="${_ini_cache[$1]}" line
  [[ -z "$content" ]] && return 0

  while IFS= read -r line; do
    [[ -n "$line" ]] && load_script "$line"
  done <<< "$content"
}
