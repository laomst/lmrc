# 文件系统操作

# 创建目录并进入
function mkcd {
    param([Parameter(Mandatory)][string]$Path)
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
    Set-Location $Path
}

# 快速回退目录
function back {
    param([int]$Count = 1)
    $path = "../" * $Count
    Set-Location $path
}

# 查找命令路径（Get-Command 的快捷封装）
function which {
    param([Parameter(Mandatory)][string]$Name)
    Get-Command $Name -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
}
