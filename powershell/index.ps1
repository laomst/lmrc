# PowerShell 环境配置入口文件

# 获取脚本所在目录
$script:_LMRC_DIR = $PSScriptRoot

# 设置 includes.ini 配置文件路径
$script:_LMRC_INCLUDES_INI = Join-Path $script:_LMRC_DIR "includes.ini"

# 加载预加载模块
. (Join-Path $script:_LMRC_DIR "include.ps1")

# ============================================
# 第一阶段：exports（环境变量配置）
# ============================================
Load-LmrcSection "pre_export"
Load-LmrcScript (Join-Path $script:_LMRC_DIR "exports.ps1")
Load-LmrcSection "post_export"

# ============================================
# 第二阶段：path（PATH 环境变量配置）
# ============================================
Load-LmrcSection "pre_path"
Load-LmrcScript (Join-Path $script:_LMRC_DIR "path.ps1")
Load-LmrcSection "post_path"

# ============================================
# 第三阶段：function（自定义函数）
# ============================================
Load-LmrcSection "pre_function"
Load-LmrcScript (Join-Path $script:_LMRC_DIR "function.ps1")
Load-LmrcSection "post_function"

# ============================================
# 第四阶段：alias（命令别名）
# ============================================
Load-LmrcSection "pre_alias"
Load-LmrcScript (Join-Path $script:_LMRC_DIR "alias.ps1")
Load-LmrcSection "post_alias"

# ============================================
# 第五阶段：completion（自动补全）
# ============================================
Load-LmrcSection "pre_completion"
Load-LmrcScript (Join-Path $script:_LMRC_DIR "completion.ps1")
Load-LmrcSection "post_completion"

# ============================================
# 第六阶段：prompt（提示符定制）
# ============================================
Load-LmrcSection "pre_prompt"
Load-LmrcScript (Join-Path $script:_LMRC_DIR "prompt.ps1")
Load-LmrcSection "post_prompt"

# ============================================
# 加载目录下其他配置文件
# ============================================
Load-LmrcSection "pre_others"

$_skipFiles = @(
    "index.ps1"
    "include.ps1"
    "exports.ps1"
    "path.ps1"
    "function.ps1"
    "alias.ps1"
    "completion.ps1"
    "prompt.ps1"
)

foreach ($_configFile in Get-ChildItem "$script:_LMRC_DIR/*.ps1" -ErrorAction SilentlyContinue) {
    if ($_configFile.Name -notin $_skipFiles) {
        Load-LmrcScript $_configFile.FullName
    }
}

Load-LmrcSection "post_others"

# ============================================
# 所有配置加载完成后
# ============================================
Load-LmrcSection "post_all"

# 清理临时变量和函数
Remove-Variable _LMRC_DIR, _LMRC_INCLUDES_INI, _skipFiles, _configFile -Scope Script -ErrorAction SilentlyContinue
Remove-Variable _ini_cache, _ini_loaded -Scope Script -ErrorAction SilentlyContinue
Remove-Item Function:Load-LmrcScript -ErrorAction SilentlyContinue
Remove-Item Function:Load-LmrcSection -ErrorAction SilentlyContinue
Remove-Item Function:_Parse-LmrcIni -ErrorAction SilentlyContinue
