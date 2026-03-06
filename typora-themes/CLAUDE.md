# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个名为 "vue-laomst" 的 Typora 自定义主题项目，提供亮色和暗色两个变体。主题以 Vue.js 品牌色（#42b983）为主色调，纯 CSS 实现，无构建系统、无依赖。

## 主题架构

### 入口与色彩系统

两个入口文件决定主题变体：
- `vue-laomst.css` → 引入 `default-color-theme.css`（亮色）+ `index.css`
- `vue-laomst-dark.css` → 引入 `dark-color-theme.css`（暗色）+ `index.css`

暗色主题通过覆盖 CSS 变量实现，不修改组件样式。所有颜色定义在 `:root` 的 CSS 自定义属性中（约 162 个变量），分为基础色、背景色、文字色、CodeMirror 语法高亮、边框色、标题渐变、特殊色七类。

### 组件结构

`vue-laomst/index.css` 汇总引入所有组件，每个 Markdown 元素类型独立一个目录/文件：

| 目录 | 用途 |
|------|------|
| `font-family/` | 字体定义（含 Monaco 字体文件） |
| `headline/` | 标题样式，`cool-headline.css` 实现渐变背景和自动层级编号 |
| `a/` | 链接样式 |
| `blockquote/` | 引用块及增强标题 |
| `code-block/` | 代码块 + gitlib (Dracula) 语法高亮 |
| `code-line/` | 行内代码 |
| `table/` | 表格 |
| `ul-ol/` | 列表 |
| `highlight/` | 高亮/mark 标记 |
| `foot-note/` | 脚注 |
| `outline/` | 大纲/目录 |

## 开发要点

- **无构建流程**：直接编辑 CSS 文件，将主题文件放入 Typora 主题目录即可预览
- **新增样式**：在 `vue-laomst/` 下创建对应目录和 CSS 文件，然后在 `index.css` 中 `@import`
- **颜色修改**：只需修改 `default-color-theme.css` 或 `dark-color-theme.css` 中的 CSS 变量，组件样式通过变量引用自动适配