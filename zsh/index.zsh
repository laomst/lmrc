#!/bin/zsh
# Zsh 环境配置入口文件

# 获取脚本所在目录
typeset -g SCRIPT_DIR="${0:A:h}"

# 设置 includes.ini 配置文件路径
typeset -g _LMRC_INCLUDES_INI="$SCRIPT_DIR/includes.ini"

# 加载预加载模块
# shellcheck disable=SC1091
source "$SCRIPT_DIR/include.zsh"

# ============================================
# 第一阶段：pre_export
# ============================================
load_section "pre_export"

# ============================================
# 第二阶段：加载 exports.zsh（环境变量配置）
# ============================================
load_script "$SCRIPT_DIR/exports.zsh"

# ============================================
# 第三阶段：post_export（exports 之后加载）
# ============================================
load_section "post_export"

# ============================================
# 第四阶段：加载核心配置文件
# ============================================

# 4.1 加载 path.zsh（PATH 环境变量配置）
load_section "pre_path"
load_script "$SCRIPT_DIR/path.zsh"
load_section "post_path"

# 4.2 加载 function.zsh（自定义函数）
load_section "pre_function"
load_script "$SCRIPT_DIR/function.zsh"
load_section "post_function"

# 4.3 加载 alias.zsh（命令别名）
load_section "pre_alias"
load_script "$SCRIPT_DIR/alias.zsh"
load_section "post_alias"

# 4.4 加载 completion.zsh（自动补全）
load_section "pre_completion"
load_script "$SCRIPT_DIR/completion.zsh"
load_section "post_completion"

# 4.5 加载 prompt.zsh（提示符定制）
load_section "pre_prompt"
load_script "$SCRIPT_DIR/prompt.zsh"
load_section "post_prompt"

# ============================================
# 第五阶段：加载目录下其他配置文件
# ============================================
load_section "pre_others"
{
  setopt LOCAL_OPTIONS NULL_GLOB
  typeset -a skip_files=(
    "index.zsh"
    "include.zsh"
    "exports.zsh"
    "path.zsh"
    "function.zsh"
    "alias.zsh"
    "completion.zsh"
    "prompt.zsh"
  )

  for config_file in "$SCRIPT_DIR"/*.zsh; do
    filename="${config_file:t}"
    (( ${skip_files[(Ie)$filename]} )) && continue
    load_script "$config_file"
  done
}
load_section "post_others"

# ============================================
# 第六阶段：post_all（所有配置加载完成后）
# ============================================
load_section "post_all"

# 清理临时变量和函数
unset SCRIPT_DIR config_file filename skip_files
unset -f load_script load_section _parse_ini
unset _ini_cache _ini_loaded _LMRC_INCLUDES_INI
