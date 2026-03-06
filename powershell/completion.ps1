# 自动补全配置

# 配置 PSReadLine 补全行为（仅在模块可用时加载）
if (Get-Module -ListAvailable PSReadLine -ErrorAction SilentlyContinue) {
    # Tab 键使用菜单补全模式
    Set-PSReadLineKeyHandler -Key Tab -Function MenuComplete

    # 上下箭头按历史前缀搜索
    Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
    Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward

    # 启用预测式自动补全（PowerShell 7.1+）
    if ($PSVersionTable.PSVersion.Major -ge 7) {
        Set-PSReadLineOption -PredictionSource History
        Set-PSReadLineOption -PredictionViewStyle ListView
    }
}

# Git 分支补全示例
Register-ArgumentCompleter -CommandName git -Native -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    # 仅在 git checkout/switch 后补全分支名
    $command = $commandAst.ToString()
    if ($command -match 'git\s+(checkout|switch)\s+') {
        git branch --format='%(refname:short)' 2>$null |
            Where-Object { $_ -like "$wordToComplete*" } |
            ForEach-Object {
                [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
            }
    }
}
