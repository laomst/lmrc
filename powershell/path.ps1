# PATH 环境变量配置
#
# 机器相关的环境变量（SDK_HOME_DIR、JAVA_HOME、MAVEN_HOME 等）
# 应在 exports.ps1 中定义

# 自定义路径（按优先级排序）
$_customPaths = @(
    "$HOME\.local\bin"
    $(if ($env:MAVEN_HOME) { "$env:MAVEN_HOME\bin" })
    $(if ($env:JAVA_HOME) { "$env:JAVA_HOME\bin" })
    $(if ($env:PYTHON_HOME) { "$env:PYTHON_HOME" })
)

# 过滤存在的目录，拼接后追加到 PATH 前部
$_newPaths = @()
foreach ($_p in $_customPaths) {
    if ($_p -and (Test-Path $_p -PathType Container)) {
        $_newPaths += $_p
    }
}

if ($_newPaths.Count -gt 0) {
    $env:LMRC_PATH = $_newPaths -join ";"
    $env:PATH = "$env:LMRC_PATH;$env:PATH"
}

Remove-Variable _customPaths, _newPaths, _p -ErrorAction SilentlyContinue
