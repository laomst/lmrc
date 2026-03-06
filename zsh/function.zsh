#!/bin/zsh
# 自定义函数库
# 自动加载 functions 目录下的所有 .zsh 文件

typeset -g _func_dir="${0:A:h}/functions"

if [[ -d "$_func_dir" ]]; then
  setopt LOCAL_OPTIONS NULL_GLOB
  for _func_file in "$_func_dir"/*.zsh; do
    source "$_func_file"
  done
fi
