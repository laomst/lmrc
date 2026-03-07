# 公共工具函数

# 检测环境变量是否存在值
# 用法: Check-EnvExists "JAVA_HOME" "GOPATH" "NODE_HOME"
# 所有变量都有值时返回 $true，否则打印缺失的变量名并返回 $false
function Check-EnvExists {
    param(
        [Parameter(Mandatory, ValueFromRemainingArguments)]
        [string[]]$Names
    )

    $missing = @()
    foreach ($name in $Names) {
        $value = [System.Environment]::GetEnvironmentVariable($name)
        if ([string]::IsNullOrWhiteSpace($value)) {
            $missing += $name
        }
    }

    if ($missing.Count -eq 0) {
        return $true
    }

    foreach ($name in $missing) {
        Write-Host "环境变量未设置: $name" -ForegroundColor Red
    }
    return $false
}
