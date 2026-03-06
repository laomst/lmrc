# Windows 服务安装指南 (NSSM)

在 Windows 上，可以使用 **NSSM (Non-Sucking Service Manager)** 将监控脚本安装为 Windows 服务。

## 安装步骤

### 1. 安装 NSSM

1. 从 [NSSM 官网](https://nssm.cc/download) 下载最新版本
2. 解压到某个目录，例如 `C:\nssm\`
3. 将 `C:\nssm\` 添加到系统 PATH 环境变量

### 2. 安装 Python 和依赖

```cmd
# 确保 Python 已安装
python --version

# 安装 watchdog
pip install watchdog
```

### 3. 使用 NSSM 安装服务

打开 **命令提示符（管理员）**，执行以下命令：

```cmd
# 设置工作空间路径（替换为你的实际路径）
set TYPORA_WORKSPACE=D:\Path\To\Typora\Workspace

# 设置脚本路径
set SCRIPT_DIR=D:\Path\To\typora-ext\scripts

# 安装服务
nssm install TyporaWatch python "%SCRIPT_DIR%\watch_workspace.py"

# 设置环境变量
nssm set TyporaWatch AppEnvironmentExtra "TYPORA_WORKSPACE=%TYPORA_WORKSPACE%"

# 设置工作目录
nssm set TyporaWatch AppDirectory "%SCRIPT_DIR%"

# 设置服务为自动启动
nssm set TyporaWatch Start SERVICE_AUTO_START

# 启动服务
nssm start TyporaWatch
```

### 4. 服务管理命令

```cmd
# 启动服务
nssm start TyporaWatch

# 停止服务
nssm stop TyporaWatch

# 重启服务
nssm restart TyporaWatch

# 查看状态
nssm status TyporaWatch

# 卸载服务
nssm remove TyporaWatch confirm
```

### 5. 查看日志

日志文件位于：`%USERPROFILE%\.typora-ext-watch.log`

## 替代方案：任务计划程序

如果不想使用 NSSM，也可以使用 Windows 任务计划程序：

1. 打开「任务计划程序」
2. 创建基本任务
3. 触发器：启动时
4. 操作：启动程序
   - 程序：`python`
   - 参数：`D:\Path\To\typora-ext\scripts\watch_workspace.py`
   - 起始于：`D:\Path\To\typora-ext\scripts`
5. 设置环境变量：`TYPORA_WORKSPACE=D:\Path\To\Typora\Workspace`
