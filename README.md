# lmrc - Laomst's RC

个人配置工具仓库，包含 Bash、Zsh Shell 配置和 Typora Markdown 编辑器扩展工具。

## ⚠️ 重要：安装位置要求

**本项目必须放置在用户家目录 (`~`) 下才能正常使用！**

### 方式一：直接放置（推荐）

将项目克隆或复制到用户家目录：

```bash
cd ~
git clone <repository-url> lmrc
# 或
cp -r /path/to/lmrc ~/lmrc
```

最终路径应为：`~/lmrc/`

### 方式二：符号链接

如果项目在其他位置，可以创建符号链接：

```bash
# 假设项目在 ~/Projects/lmrc
ln -s ~/Projects/lmrc ~/lmrc
```

**为什么必须在家目录下？**

配置文件中的路径硬编码了 `~/lmrc` 路径（如 `source ~/lmrc/bash/index.sh`）。如果项目在其他位置，需要手动修改所有路径引用。

---

## 项目结构

```
lmrc/
├── bash/          # Bash Shell 配置（Linux/macOS）
├── zsh/           # Zsh Shell 配置（Linux/macOS）
├── typora/        # Typora 扩展工具（跨平台）
├── README.md      # 项目说明
└── CLAUDE.md      # Claude Code 工作指南
```

## 快速开始

### 安装 Bash 配置

在 `~/.bashrc` (Linux/WSL) 或 `~/.bash_profile` (macOS) 中添加：

```bash
source ~/lmrc/bash/index.sh
```

### 安装 Zsh 配置

在 `~/.zshrc` 中添加：

```bash
source ~/lmrc/zsh/index.zsh
```

### 使用 Typora 扩展

参考 [typora/README.md](typora/README.md)

## 平台支持

| 组件 | Linux | macOS | Windows | WSL |
|------|-------|-------|---------|-----|
| Bash 配置 | ✅ | ✅ | ❌ | ✅ |
| Zsh 配置 | ✅ | ✅ | ❌ | ✅ |
| Typora 扩展 | ✅ | ✅ | ✅ | ✅ |

> **注意：** Bash/Zsh 配置不支持原生 Windows，Windows 用户请使用 WSL。

## 文档

- [CLAUDE.md](CLAUDE.md) - Claude Code 工作指南
- [bash/README.md](bash/README.md) - Bash 配置详细说明
- [zsh/README.md](zsh/README.md) - Zsh 配置详细说明
- [typora/README.md](typora/README.md) - Typora 扩展使用说明

## 许可

个人配置，仅供参考使用。
