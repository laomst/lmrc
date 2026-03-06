# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 AutoHotkey v2 脚本项目，用于在 Windows 上模拟 macOS 键盘操作习惯。

脚本文件：`laomst-ahk-script.ahk`（需要 AutoHotkey v2.0+）

## 脚本功能

- NumLock 永远开启
- PgUp/PgDn 映射为 Home/End
- Alt+C/V/X/Z/A/S 映射为对应的 Ctrl 组合键（模拟 macOS 的 Cmd 键行为）
- CapsLock 需长按 0.5 秒才生效，防止误触（含修饰键组合的防误触处理）

## 语法要求

使用 AutoHotkey v2 语法（`#Requires AutoHotkey v2.0`），注意与 v1 的区别：
- 函数调用使用括号：`KeyWait("CapsLock","T0.5")`
- 热键块使用 `::{}` 大括号语法
- 字符串使用双引号
