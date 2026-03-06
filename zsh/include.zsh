#!/bin/zsh
# includes 模块加载器
# 自动加载 includes 目录下的所有 .zsh 文件

typeset -g _includes_dir="${0:A:h}/includes"

if [[ -d "$_includes_dir" ]]; then
  setopt LOCAL_OPTIONS NULL_GLOB
  for _includes_file in "$_includes_dir"/*.zsh; do
    source "$_includes_file"
  done
fi
