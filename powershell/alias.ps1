# 命令别名配置

# ls 别名
Set-Alias -Name ll -Value Get-ChildItem
Set-Alias -Name la -Value Get-ChildItem

# 常用工具
Set-Alias -Name cls -Value Clear-Host
Set-Alias -Name open -Value Invoke-Item

# Git 别名（简单命令用 Set-Alias，带参数的用函数包装）
function gs { git status $args }
function ga { git add $args }
function gc { git commit $args }
function gp { git push $args }
function gl { git log --oneline -20 $args }

# 目录跳转函数
function .. { Set-Location .. }
function ... { Set-Location ../.. }
