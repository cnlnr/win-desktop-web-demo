# win-desktop-web-demo

把Windows的GUI桌面换成 Web

壁纸引擎出现自动消失的问题，我无法修复，已经去掉这个功能 <https://gitee.com/LZY4/win-desktop-web-demo/commit/a3d5e9728ca33e3be4e3ee9cb8c8aad3c9be70cc>

## 原理流程

``` text
寻找桌面hwnd -> 寻找pywebview的hwnd -> 挂载pywebview到桌面hwnd -> web显示桌面GUI并与python交互
```
