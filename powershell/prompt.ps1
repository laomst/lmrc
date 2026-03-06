# 提示符配置

# 覆盖 prompt 全局函数
# 显示格式：[HH:mm:ss] user@hostname:dir [git-branch] >
function global:prompt {
    $lastSuccess = $?
    $esc = [char]27

    # 时间
    $time = Get-Date -Format "HH:mm:ss"

    # 用户和主机名
    $user = $env:USERNAME
    if (-not $user) { $user = $env:USER }
    $hostname = $env:COMPUTERNAME
    if (-not $hostname) { $hostname = (hostname) }

    # 当前目录（仅显示最后一级）
    $dir = Split-Path -Leaf (Get-Location)
    if (-not $dir) { $dir = (Get-Location).Path }

    # Git 分支
    $gitBranch = ""
    $branch = git branch --show-current 2>$null
    if ($branch) {
        $gitBranch = " $esc[33m[$branch]$esc[0m"
    }

    # 状态符号（成功绿色 >，失败红色 >）
    if ($lastSuccess) {
        $indicator = "$esc[32m>$esc[0m"
    } else {
        $indicator = "$esc[31m>$esc[0m"
    }

    # 拼接提示符
    "$esc[1;34m[$time]$esc[0m $esc[32m$user$esc[0m@$esc[33m$hostname$esc[0m:$esc[1;36m$dir$esc[0m$gitBranch $indicator "
}
