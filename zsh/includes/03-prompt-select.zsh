#!/bin/zsh
# 通用交互式选择菜单
# 用法: prompt-select "标题" "key1:描述1" "key2:描述2" ...
# 结果: 选中的 key 存入 REPLY；选择退出或 Ctrl+C 返回非零值
prompt-select() {
  local title=$1
  shift
  local options=("$@" "quit:退出")

  # 临时关闭调试模式
  local _sm_old_xtrace=$([[ $- == *x* ]] && echo "on" || echo "off")
  local _sm_old_ps4=$PS4
  set +xv
  PS4=''
  unsetopt XTRACE VERBOSE 2>/dev/null

  # 屏蔽输入回显
  local _sm_old_stty=$(stty -g 2>/dev/null)
  stty -echo 2>/dev/null

  local keys=() descs=()
  for opt in "${options[@]}"; do
    keys+=("${opt%%:*}")
    descs+=("${opt#*:}")
  done

  local selected=0
  local num_options=${#options[@]}
  local _num_buf=""
  local _menu_lines=$((num_options + 4))
  local _menu_drawn=""

  # 清理函数：擦除菜单并恢复终端状态
  _sm_cleanup() {
    [[ -n "$_menu_drawn" ]] && printf '\033[%dA\033[J' "$_menu_lines"
    tput cnorm 2>/dev/null
    stty "$_sm_old_stty" 2>/dev/null
    unfunction _sm_draw _sm_cleanup 2>/dev/null
    trap - INT
  }
  trap '_sm_cleanup; [[ "$_sm_old_xtrace" == "on" ]] && set -x && setopt XTRACE VERBOSE 2>/dev/null; PS4=$_sm_old_ps4; return 130' INT

  # 隐藏光标
  tput civis 2>/dev/null

  # 绘制菜单
  _sm_draw() {
    [[ -n "$_menu_drawn" ]] && printf '\033[%dA' "$_menu_lines"
    _menu_drawn=1
    printf '\033[K\n'
    printf '\033[1;36m  === %s ===\033[0m\033[K\n' "$title"
    if [[ -n "$_num_buf" ]]; then
      if (( _num_buf >= 1 && _num_buf <= num_options )); then
        # 数字有效
        printf '\033[38;2;160;205;255m  [跳转到: \033[1;33m%s\033[0;38;2;160;205;255m | 回车跳转 | 退格修改 | Esc清空]\033[0m\033[K\n' "$_num_buf"
      else
        # 数字超出范围
        printf '\033[38;2;160;205;255m  [跳转到: \033[1;31m%s (无效，范围 1-%d)\033[0;38;2;160;205;255m | 退格修改 | Esc清空]\033[0m\033[K\n' "$_num_buf" "$num_options"
      fi
    else
      printf '\033[38;2;160;205;255m  [↑↓ 选择 | 数字快选 | 回车确认 | Esc退出]\033[0m\033[K\n'
    fi
    printf '\033[K\n'
    for i in {1..$num_options}; do
      if [[ $i -eq $((selected + 1)) ]]; then
        printf '\033[1;34m> %d. %s\033[0m\033[K\n' "$i" "${descs[$i]}"
      else
        printf '\033[90m  %d. %s\033[0m\033[K\n' "$i" "${descs[$i]}"
      fi
    done
  }

  _sm_draw

  local input seq selected_key
  while true; do
    input=''
    read -sk 1 input 2>/dev/null
    case $input in
      $'\x1b')
        seq=''
        read -sk 2 -t 0.001 seq 2>/dev/null
        if [[ -n "$_num_buf" ]]; then
          # 数字输入模式下按 Esc：清空数字缓冲区
          if [[ -z "$seq" ]]; then
            _num_buf=""
            _sm_draw
          fi
        else
          case $seq in
            '[A') ((selected--)); ((selected < 0)) && selected=$((num_options - 1)); _sm_draw ;;
            '[B') ((selected++)); ((selected >= num_options)) && selected=0; _sm_draw ;;
            # 普通模式下按 Esc：取消选择
            '') selected_key="quit"; break ;;
          esac
        fi
        ;;
      ''|$'\x0d'|$'\x0a')
        if [[ -n "$_num_buf" ]]; then
          # 数字输入模式下按回车：跳转到对应选项
          if (( _num_buf >= 1 && _num_buf <= num_options )); then
            selected=$((_num_buf - 1))
          fi
          _num_buf=""
          _sm_draw
        else
          # 普通模式下按回车：确认当前选项
          selected_key="${keys[$((selected + 1))]}"
          break
        fi
        ;;
      # 退格键：删除数字缓冲区最后一位
      $'\x7f'|$'\x08')
        if [[ -n "$_num_buf" ]]; then
          _num_buf="${_num_buf%?}"
          _sm_draw
        fi
        ;;
      # 数字键：追加到数字缓冲区
      [0-9])
        _num_buf="${_num_buf}${input}"
        _sm_draw
        ;;
      *) continue ;;
    esac
  done

  _sm_cleanup

  # 恢复调试设置
  [[ "$_sm_old_xtrace" == "on" ]] && set -x
  [[ "$_sm_old_xtrace" == "on" ]] && setopt XTRACE VERBOSE 2>/dev/null
  PS4=$_sm_old_ps4

  [[ "$selected_key" == "quit" ]] && { printf '\033[1;31m已取消选择\033[0m\n'; return 1; }
  printf '\033[1;32m已选择 => %s\033[0m\n' "${descs[$((selected + 1))]}"
  REPLY=$selected_key
}
