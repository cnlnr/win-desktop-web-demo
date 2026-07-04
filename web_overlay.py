import time
import threading
import win32api
import win32con
import win32gui


def overlay(window_obj):
    time.sleep(1)  # 等待 webview 完全初始化

    def _detach():
        # === 1. 完全参考你的方法获取主窗口 HWND ===
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

        # === 2. 完全参考你的方法获取内部 Chrome 内核 HWND ===
        chrome_h = None
        for _ in range(100):
            chrome_hwnds = []

            def callback(hwnd, extra):
                if win32gui.GetClassName(hwnd) == "Chrome_WidgetWin_1":
                    chrome_hwnds.append(hwnd)
                    return False
                return True

            win32gui.EnumChildWindows(main_h, callback, None)
            chrome_h = chrome_hwnds[0] if chrome_hwnds else None
            if chrome_h and win32gui.IsWindowVisible(main_h):
                break
            time.sleep(0.1)

        if not chrome_h:
            return

        # === 3. 获取当前窗口原本的坐标与尺寸 ===
        rect = win32gui.GetWindowRect(main_h)
        x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]

        # === 4. 获取 Windows 桌面底层 WorkerW 壁纸句柄 ===
        progman = win32gui.FindWindow("Progman", "Program Manager")
        win32gui.SendMessageTimeout(
            progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)

        desktop_h = [progman]

        def enum_proc(hwnd, lParam):
            if win32gui.GetClassName(hwnd) == "WorkerW" and win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None):
                next_worker = win32gui.FindWindowEx(0, hwnd, "WorkerW", None)
                if next_worker:
                    desktop_h[0] = next_worker
                    return False
            return True
        win32gui.EnumWindows(enum_proc, 0)

        # === 5. 将 web 层直接挂载到桌面底层 ===
        style = win32gui.GetWindowLong(chrome_h, win32con.GWL_STYLE)
        # 修改为子窗口样式
        new_style = (style & ~win32con.WS_POPUP) | win32con.WS_CHILD
        win32gui.SetWindowLong(chrome_h, win32con.GWL_STYLE, new_style)

        win32gui.SetParent(chrome_h, desktop_h[0])  # 强行挂载到桌面 WorkerW 内部

        # 保持你在 main.py 里 create_window 的原大小和原位置钉在桌面上
        win32gui.SetWindowPos(
            chrome_h, 0, x, y, w, h,
            win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW
        )

        # === 6. 隐藏原本的 pywebview 壳窗口 ===
        win32gui.ShowWindow(main_h, win32con.SW_HIDE)
        ex_style = win32gui.GetWindowLong(main_h, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(main_h, win32con.GWL_EXSTYLE,
                               ex_style | win32con.WS_EX_TOOLWINDOW)

    threading.Thread(target=_detach, daemon=True).start()
