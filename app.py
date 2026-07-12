import webview
import win32gui
import win32con
import threading
import time


def mount_logic(window_obj):
    """纯粹的桌面全屏挂载逻辑，移除了所有 API 交互"""
    # 1. 获取 pywebview 的原生主窗口句柄
    main_h = None
    for _ in range(100):
        if window_obj.native is not None:
            try:
                main_h = window_obj.native.Handle.ToInt32()
                if main_h:
                    break
            except:
                pass
        time.sleep(0.1)

    if not main_h:
        return

    # 2. 寻找真正的 Windows 桌面底层句柄 (Progman 或 WorkerW)
    progman = win32gui.FindWindow("Progman", "Program Manager")
    desktop_hwnd = None

    def enum_windows_proc(hwnd, extra):
        nonlocal desktop_hwnd
        if win32gui.GetClassName(hwnd) == "WorkerW":
            shell_dll = win32gui.FindWindowEx(
                hwnd, 0, "SHELLDLL_DefView", None)
            if shell_dll:
                desktop_hwnd = win32gui.FindWindowEx(0, hwnd, "WorkerW", None)
        return True

    win32gui.EnumWindows(enum_windows_proc, None)
    if not desktop_hwnd:
        desktop_hwnd = progman

    # 3. 寻找内部的浏览器渲染内核句柄 (Chrome_WidgetWin_1)
    for i in range(100):
        chrome_hwnds = []

        def callback(hwnd, extra):
            if win32gui.GetClassName(hwnd) == "Chrome_WidgetWin_1":
                chrome_hwnds.append(hwnd)
                return False
            return True

        win32gui.EnumChildWindows(main_h, callback, None)
        target_hwnd = chrome_hwnds[0] if chrome_hwnds else None

        if target_hwnd and win32gui.IsWindowVisible(main_h):
            # 获取外壳窗口全屏后的实际全屏尺寸
            rect = win32gui.GetWindowRect(main_h)
            x, y, w, h = rect[0], rect[1], rect[2]-rect[0], rect[3]-rect[1]

            # 4. 将样式修改为“子窗口 (WS_CHILD)”，去除独立悬浮属性
            style = win32gui.GetWindowLong(target_hwnd, win32con.GWL_STYLE)
            new_style = (style & ~win32con.WS_POPUP) | win32con.WS_CHILD
            win32gui.SetWindowLong(target_hwnd, win32con.GWL_STYLE, new_style)

            # 5. 将父窗口强制绑定到系统桌面句柄上
            win32gui.SetParent(target_hwnd, desktop_hwnd)

            # 6. 调整 Z 轴排序：使用 HWND_TOP 确保在桌面最顶层（壁纸和图标之上）
            win32gui.SetWindowPos(
                target_hwnd,
                win32con.HWND_TOP,
                x, y, w, h,
                win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
            )

            # 7. 强行刷新并显示 WebView
            win32gui.ShowWindow(target_hwnd, win32con.SW_SHOW)
            win32gui.UpdateWindow(target_hwnd)

            # 8. 隐藏 pywebview 原生生成的外壳空窗口
            win32gui.ShowWindow(main_h, win32con.SW_HIDE)
            break
        time.sleep(0.1)


if __name__ == '__main__':
    # 在这里填入你需要全屏展示的 Web 网址
    TARGET_URL = 'https://html5test.co'

    window = webview.create_window(
        'DesktopWidget',
        url=TARGET_URL,
        transparent=True,       # 允许网页透明背景
        fullscreen=True         # 全屏启动
    )

    # 异步执行全屏挂载
    threading.Thread(target=mount_logic, args=(window,), daemon=True).start()
    webview.start()
