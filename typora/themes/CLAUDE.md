# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是 **vue-laomst**，一个受 Vue.js 美学启发的自定义 Typora 主题。Typora 是一个使用 CSS 主题进行样式的 Markdown 编辑器。本项目仅包含 CSS - 没有构建工具、包管理器或编译步骤。

主题支持亮色和暗黑两种模式，通过颜色主题变量系统实现。

## 架构

### 入口点
- `vue-laomst.css` - 亮色主题入口文件
- `vue-laomst-dark.css` - 暗黑主题入口文件

### 文件结构
```
themes/
├── vue-laomst.css              # 亮色主题入口
├── vue-laomst-dark.css         # 暗黑主题入口
├── CLAUDE.md                   # 本文件
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

### 主题加载顺序

入口文件加载顺序：
1. 颜色主题 (`default-color-theme.css` 或 `dark-color-theme.css`)
2. 全局样式 (`index.css`)

`index.css` 包含：
- 所有模块的 `@import` 语句
- `:root` 变量定义（兼容 Typora）
- 全局样式（html, body, #write 等）

### 模块化 CSS 结构
主题按功能模块组织在 `vue-laomst/` 目录下：
- `font-family/` - 字体定义（内嵌 base64 的 Monaco 字体）
- `headline/` - 标题样式（H1-H6）支持自动层级编号
- `blockquote/` - 引用块样式，支持标题
- `code-block/` - 代码块语法高亮（使用 gitlib 主题）
- `code-line/` - 行内代码样式
- `ul-ol/` - 列表样式（有序和无序）
- `table/` - 表格格式化
- `a/` - 锚点/链接样式
- `foot-note/` - 脚注格式化
- `outline/` - 文档大纲样式
- `heigh-light/` - 文本高亮样式

### 颜色主题系统

主题使用 CSS 变量实现颜色主题切换。颜色变量按功能分类：

- `--color-*` - 基础颜色
- `--bg-*` - 背景色
- `--text-*` - 文字颜色
- `--cm-*` - 代码块颜色
- `--border-*` - 边框颜色
- `--header-*` - 标题渐变
- `--badge-bg`, `--outline-badge-bg` - 特殊颜色

### 样式变体系统

每个模块文件夹包含：
1. 一个索引文件（如 `blockquote.css`、`code-block.css`），用于导入特定变体
2. 一个或多个变体 CSS 文件，可通过修改 `@import` 语句来切换

例如，切换代码块主题：
- 编辑 `vue-laomst/code-block/code-block.css`
- 将 `@import` 从 `./gitlib.css` 改为其他变体

### 关键设计模式

1. **基于 CSS 计数器的标题编号**：标题使用 CSS 计数器显示层级数字（H1:1, H2:1.1, H3:1.1.1 等），定义在 `headline/cool-headline.css`

2. **特殊页脚标记**：
   - `#write::after` 添加"文章结尾"标记
   - 最后一个引用块通过特殊选择器样式化为"参考文献"部分

3. **Typora 特定覆盖**：许多样式覆盖了来自 `base-control.css` 的 Typora 基础样式（如 `h3.md-focus:before` 覆盖）

4. **打印媒体查询**：主题包含 `@media print` 规则以优化打印效果

## 常见开发任务

### 测试主题更改

**方式一：使用软连接（推荐）**

软连接方式可以实时同步主题更改，无需重复复制：

```bash
# macOS/Linux
cd ~/Library/Application\ Support/abnerworks.Typora/themes/
ln -s ~/lmrc/typora/themes/vue-laomst.css vue-laomst.css
ln -s ~/lmrc/typora/themes/vue-laomst-dark.css vue-laomst-dark.css
ln -s ~/lmrc/typora/themes/vue-laomst vue-laomst
```

**方式二：复制文件**

```bash
# 复制入口文件和主题模块目录
cp ~/lmrc/typora/themes/vue-laomst.css ~/Library/Application\ Support/abnerworks.Typora/themes/
cp ~/lmrc/typora/themes/vue-laomst-dark.css ~/Library/Application\ Support/abnerworks.Typora/themes/
cp -r ~/lmrc/typora/themes/vue-laomst ~/Library/Application\ Support/abnerworks.Typora/themes/
```

**Windows 用户：** 将文件复制到 `%APPDATA%\Typora\themes\` 目录

完成后重启 Typora 并从主题菜单中选择对应主题。

### 添加新的样式变体
1. 在相应的模块文件夹中创建新的 CSS 文件（如 `headline/new-variant.css`）
2. 更新模块的索引文件以导入新变体：
   ```css
   @import './new-variant.css';
   ```

### 创建新颜色主题
1. 复制 `default-color-theme.css` 或 `dark-color-theme.css`
2. 修改颜色变量值
3. 创建新的入口文件，导入新颜色主题和 `index.css`

### 调整主题变量
颜色变量定义在对应的颜色主题文件中：
- `default-color-theme.css` - 亮色主题
- `dark-color-theme.css` - 暗黑主题

兼容 Typora 的变量定义在 `index.css` 的 `:root` 中：
- `--select-text-bg-color` - 文本选择高亮
- `--side-bar-bg-color` - 侧边栏背景
- `--control-text-color` - 控件文本颜色
- `--my-favorate-fonts` - 字体栈

## 重要说明

- 不存在构建过程 - CSS 文件直接被 Typora 使用
- Monaco 字体以 base64 形式内嵌在 `font-family/monaco/monaco.css` 中
- Mermaid 图表预览位置已调整以防止重叠
- 书写区域设置 `min-height: unset` 以实现灵活高度
