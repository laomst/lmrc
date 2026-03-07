# 脚本加载工具函数
# 固定加载 includes.ini 配置文件

# ============================================
# 缓存：includes.ini 的 section 内容
# ============================================
$script:_ini_cache = @{}
$script:_ini_loaded = $false

# 解析 includes.ini 并缓存
function _Parse-LmrcIni {
    if ($script:_ini_loaded) { return }
    $script:_ini_loaded = $true

    $configFile = $script:_LMRC_INCLUDES_INI
    if (-not $configFile -or -not (Test-Path $configFile)) { return }

    $currentSection = ""
    foreach ($line in Get-Content $configFile) {
        # 跳过空行和注释
        if ([string]::IsNullOrWhiteSpace($line) -or $line -match '^\s*#') { continue }

        # 检测 section
        if ($line -match '^\[([^\]]+)\]') {
            $currentSection = $Matches[1]
            $script:_ini_cache[$currentSection] = @()
            continue
        }

        # 追加路径到当前 section（仅支持绝对路径）
        # Windows 盘符（C:\）、UNC 路径（\\）、~ 或 $ 开头
        if ($currentSection -and $line -match '^[A-Za-z]:\\|^\\\\|^~|^\$') {
            $script:_ini_cache[$currentSection] += $line.Trim()
        }
    }
}

# ============================================
# 公开函数
# ============================================

# 加载单个脚本
# 用法: Load-LmrcScript "path/to/script.ps1"
function Load-LmrcScript {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return }

    # 展开 ~ 为 $HOME
    $expanded = $Path -replace '^~', $HOME
    # 展开环境变量 $env:VAR 格式
    $expanded = [System.Environment]::ExpandEnvironmentVariables(
        $expanded -replace '\$env:(\w+)', '%$1%'
    )

    if (Test-Path $expanded) {
        . $expanded
    }
}

# 加载指定 section 下的脚本
# 用法: Load-LmrcSection "section_name"
function Load-LmrcSection {
    param([string]$Section)
    _Parse-LmrcIni

    if (-not $script:_ini_cache.ContainsKey($Section)) { return }
    foreach ($scriptPath in $script:_ini_cache[$Section]) {
        if ($scriptPath) { Load-LmrcScript $scriptPath }
    }
}
