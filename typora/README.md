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

---

## Scripts

### index_typora_markdowns.py

为 Typora 工作空间中的 Markdown 文件建立索引系统。

**功能：**
- 自动添加 YAML front matter（`serial`、`typora-root-url`、`typora-copy-images-to`）
- 维护工作空间根目录的 `.index/path_index.json` 索引文件

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

## 主题

### vue-laomst 主题

一个受 Vue.js 美学启发的 Typora 主题，支持亮色和暗黑两种模式。

**主题特点：**
- 模块化 CSS 架构，易于维护和扩展
- 颜色主题变量系统，支持自定义配色
- CSS 计数器实现标题自动编号
- 代码块语法高亮（gitlib 主题）
- 响应式打印样式

**文件结构：**
```
themes/
├── vue-laomst.css              # 亮色主题入口
├── vue-laomst-dark.css         # 暗黑主题入口
├── CLAUDE.md                   # 主题开发文档
└── vue-laomst/                 # 主题模块目录
    ├── index.css               # 全局公共样式
    ├── default-color-theme.css # 亮色主题颜色变量
    ├── dark-color-theme.css    # 暗黑主题颜色变量
    ├── a/                      # 锚点/链接样式
    ├── blockquote/             # 引用块样式
    ├── code-block/             # 代码块语法高亮
    ├── code-line/              # 行内代码样式
    ├── font-family/            # 字体定义（Monaco）
    ├── foot-note/              # 脚注格式化
    ├── headline/               # 标题样式（H1-H6）
    ├── heigh-light/            # 文本高亮样式
    ├── outline/                # 文档大纲样式
    ├── table/                  # 表格格式化
    └── ul-ol/                  # 列表样式
```

#### 安装主题

**方式一：使用软连接（推荐）**

软连接方式可以实时同步主题更改，修改主题后无需重复复制：

```bash
# macOS/Linux
cd ~/Library/Application\ Support/abnerworks.Typora/themes/
ln -s ~/.lmrc/typora/themes/vue-laomst.css vue-laomst.css
ln -s ~/.lmrc/typora/themes/vue-laomst-dark.css vue-laomst-dark.css
ln -s ~/.lmrc/typora/themes/vue-laomst vue-laomst
```

**方式二：复制文件**

```bash
# 复制入口文件和主题模块目录
cp ~/.lmrc/typora/themes/vue-laomst.css ~/Library/Application\ Support/abnerworks.Typora/themes/
cp ~/.lmrc/typora/themes/vue-laomst-dark.css ~/Library/Application\ Support/abnerworks.Typora/themes/
cp -r ~/.lmrc/typora/themes/vue-laomst ~/Library/Application\ Support/abnerworks.Typora/themes/
```

**Windows 用户：** 将文件复制到 `%APPDATA%\Typora\themes\` 目录

完成后重启 Typora 并从主题菜单中选择对应主题。

#### 自定义颜色主题

1. 复制颜色主题文件：
   ```bash
   cp ~/.lmrc/typora/themes/vue-laomst/default-color-theme.css ~/lmrc/typora/themes/vue-laomst/my-color-theme.css
   ```

2. 修改颜色变量值

3. 创建新入口文件：
   ```css
   /* 颜色主题 */
   @import 'vue-laomst/my-color-theme.css';
   /* 全局样式 */
   @import 'vue-laomst/index.css';
   ```

> 详细的主题开发文档请参阅：`themes/CLAUDE.md`

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
