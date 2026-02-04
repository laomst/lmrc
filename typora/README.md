# Typora 扩展工具

Typora 编辑器的扩展工具集，包含索引管理、文件监控、快捷键和自定义主题。

## 前置要求

Python 3.7+ 和虚拟环境（macOS Sonoma 及以后需要）：

```bash
cd ~/lmrc/typora

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r scripts/requirements.txt
```

## Scripts

### index_typora_markdowns.py

为 Typora 工作空间中的 Markdown 文件建立索引系统。

**功能：**
- 自动添加 YAML front matter（`article-id`、`typora-root-url`、`typora-copy-images-to`）
- 维护工作空间根目录的 `.index.json` 索引文件

**使用方式：**
```bash
# 激活虚拟环境后运行
source ~/lmrc/typora/venv/bin/activate

# 处理单个文件
python scripts/index_typora_markdowns.py path/to/file.md

# 处理目录
python scripts/index_typora_markdowns.py path/to/directory

# 指定工作空间路径
python scripts/index_typora_markdowns.py -w /path/to/workspace path/to/file.md
```

### watch_workspace.py

**文件监控服务** - 自动监控工作空间中的 Markdown 文件变化并更新索引。

**监控事件：**
| 事件 | 处理 |
|------|------|
| 新建 | 自动添加 front matter 和索引 |
| 移动 | 自动更新索引路径 |
| 删除 | 自动从索引移除 |
| 修改 | 检查并更新（带防抖） |

**使用方式：**

**方式一：使用便捷脚本（推荐）**
```bash
# 前台运行
~/lmrc/typora/watch.sh -w /path/to/workspace

# 后台运行
~/lmrc/typora/watch.sh --daemon

# 停止服务
~/lmrc/typora/watch.sh --stop

# 查看状态
~/lmrc/typora/watch.sh --status
```

**方式二：手动激活虚拟环境**
```bash
source ~/lmrc/typora/venv/bin/activate

# 前台运行
python scripts/watch_workspace.py -w /path/to/workspace

# 后台运行
python scripts/watch_workspace.py --daemon

# 停止服务
python scripts/watch_workspace.py --stop
```

**系统服务安装：**
```bash
# Linux (systemd)
sudo service-install/install-service.sh install

# macOS (launchd) - 注意：不要使用 sudo
./service-install/install-service.sh install

# 查看完整文档
cat service-install/README.md
```

---

## 旧组件

### image_uploader
管理 markdown 文件中的图片资源，可配置 Typora 的图片上传。
```bash
python ./typora_upload_command.py ${filepath}
```

### key_mappings
快捷键配置文件

### custom_typora_themes
自定义的 Typora 主题

### custom_md2all_thmems
[md2all](http://md.aclickall.com/) 网站的自定义主题

