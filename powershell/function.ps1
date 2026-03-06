# 自定义函数库
# 自动加载 functions 目录下的所有 .ps1 文件

$_funcDir = Join-Path $PSScriptRoot "functions"

if (Test-Path $_funcDir) {
    foreach ($_funcFile in Get-ChildItem "$_funcDir/*.ps1" -ErrorAction SilentlyContinue | Sort-Object Name) {
        . $_funcFile.FullName
    }
}

Remove-Variable _funcDir, _funcFile -ErrorAction SilentlyContinue
