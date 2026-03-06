# vue-laomst — Typora 自定义主题

一款以 Vue.js 品牌色为基调的 Typora 主题，提供亮色与暗色两个变体。

## 预览

### 主要特性

- 标题渐变背景 + 自动层级编号（H1:1、H2:1.1、H2:1.2 ...）
- 代码块使用 Dracula 风格语法高亮，内置 Monaco 等宽字体
- 引用块支持内嵌标题，标题文字以 Vue 绿色标签呈现
- 文章末尾自动显示「文章结尾」标记，最后一个引用块渲染为「文章引用」区域
- YAML Front Matter 带标签头装饰
- 完整的打印样式适配

## 安装

1. 打开 Typora，进入 **偏好设置 → 外观 → 打开主题文件夹**
2. 将主题入口文件复制到主题目录，并为资源文件夹创建符号链接：

   **macOS / Linux (Bash)：**
   ```bash
   # 假设本项目路径为 /path/to/typora-themes，主题目录为 THEME_DIR
   cp vue-laomst.css vue-laomst-dark.css "$THEME_DIR/"
   ln -s /path/to/typora-themes/vue-laomst "$THEME_DIR/vue-laomst"
   ```

   **Windows (PowerShell，需以管理员身份运行)：**
   ```powershell
   # 假设本项目路径为 C:\path\to\typora-themes，主题目录为 $THEME_DIR
   Copy-Item vue-laomst.css, vue-laomst-dark.css -Destination "$THEME_DIR"
   New-Item -ItemType SymbolicLink -Path "$THEME_DIR\vue-laomst" -Target "C:\path\to\typora-themes\vue-laomst"
   ```
3. 重启 Typora，在 **主题** 菜单中选择 **Vue Laomst** 或 **Vue Laomst Dark**

## 主题结构

```
vue-laomst.css              ← 亮色主题入口
vue-laomst-dark.css         ← 暗色主题入口
vue-laomst/
├── default-color-theme.css ← 亮色配色变量（~162 个 CSS 变量）
├── dark-color-theme.css    ← 暗色配色变量（继承亮色，覆盖部分变量）
├── index.css               ← 全局样式 & 组件汇总导入
├── font-family/            ← 字体定义（Monaco 字体文件）
├── headline/               ← 标题（渐变背景 + 自动编号）
├── blockquote/             ← 引用块（含标题增强）
├── code-block/             ← 代码块（Dracula 语法高亮）
├── code-line/              ← 行内代码
├── table/                  ← 表格
├── ul-ol/                  ← 列表
├── a/                      ← 链接
├── heigh-light/            ← 高亮标记
├── foot-note/              ← 脚注
└── outline/                ← 大纲/目录
```

入口文件通过 `@import` 选择配色方案：

- `vue-laomst.css` → `default-color-theme.css` + `index.css`
- `vue-laomst-dark.css` → `dark-color-theme.css` + `index.css`

`dark-color-theme.css` 先引入 `default-color-theme.css`，再覆盖需要调整的变量，因此组件样式无需任何修改即可适配暗色模式。

## 自定义

### 修改配色

编辑 `vue-laomst/default-color-theme.css` 中的 CSS 变量即可全局调整配色。变量按以下类别组织：

| 类别 | 示例变量 |
|------|---------|
| 基础色 | `--color-vue-green`、`--color-medium-gray` |
| 背景色 | `--bg-code-block`、`--bg-blockquote`、`--bg-highlight` |
| 文字色 | `--text-primary`、`--text-link`、`--text-inline-code` |
| 语法高亮 | `--cm-keyword`、`--cm-string`、`--cm-comment` |
| 标题渐变 | `--header-gradient-start`、`--header-gradient-end` |

如需单独调整暗色主题，在 `dark-color-theme.css` 中覆盖对应变量。

### 排版参数

- 基础字号：17px（`index.css` 中 `html { font-size: 17px }`）
- 行高：1.6rem，字间距：2px
- 内容宽度：80%（`#write { max-width: 80% }`）
- 字体：Monaco → PingFang SC → Microsoft YaHei

## 写作约定

为获得最佳显示效果，请遵循以下约定：

- **文章引用**：将文章末尾的最后一个引用块（blockquote）用作参考文献区域，主题会自动将其渲染为「文章引用」样式
- **引用块标题**：在引用块内使用标题（如 `> ### 标题`），标题文字会以绿色标签样式呈现

## 许可

MIT
