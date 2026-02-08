#Requires AutoHotkey v2.0

; `NumLock`永远开启
SetNumLockState "AlwaysOn"

; pageUp和pageDown映射为Home和End
PgUp::Home
PgDn::End

; 模拟macos习惯，复制和粘贴，`alt+c` -> `shift+Insert`、`alt+v` -> `ctrl+Insert`
!c::^Insert
!v::+Insert

; 模拟macos习惯
!x::^x
!z::^z
!a::^a
!s::^s

; `CapsLock`长按生效，时间间隔0.5秒
CapsLock::{
    if (!KeyWait("CapsLock","T0.5")) {
        SetCapsLockState !GetKeyState("CapsLock", "T")
        KeyWait("CapsLock")
    }
}

; 下面几个组合键是防止误触导致的大小写切换
!CapsLock::{
    if (!KeyWait("CapsLock","T0.5") && !KeyWait("!", "T0.5")) {
        SetCapsLockState !GetKeyState("CapsLock", "T")
        KeyWait("CapsLock")
        KeyWait("!")
    }
}
^CapsLock::{
    if (!KeyWait("CapsLock","T0.5") && !KeyWait("^", "T0.5")) {
        SetCapsLockState !GetKeyState("CapsLock", "T")
        KeyWait("CapsLock")
        KeyWait("^")
    }
}
+CapsLock::{
    if (!KeyWait("CapsLock","T0.5") && !KeyWait("+", "T0.5")) {
        SetCapsLockState !GetKeyState("CapsLock", "T")
        KeyWait("CapsLock")
        KeyWait("+")
    }
}