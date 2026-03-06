# includes 模块加载器
# 自动加载 includes 目录下的所有 .ps1 文件

$_includesDir = Join-Path $PSScriptRoot "includes"

if (Test-Path $_includesDir) {
    foreach ($_includesFile in Get-ChildItem "$_includesDir/*.ps1" -ErrorAction SilentlyContinue | Sort-Object Name) {
        . $_includesFile.FullName
    }
}

Remove-Variable _includesDir, _includesFile -ErrorAction SilentlyContinue
