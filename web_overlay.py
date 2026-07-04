import time
import threading
import win32con
import win32gui
import desktop_finder  # 引入上面的寻找库


def overlay(window_obj, mode="below_icon"):  # 可以默认或者在 main 里控制传参
    time.sleep(1)  # 等待加载完成

    def _detach():
        # === 1. 严格参考你的方法获取主窗口 HWND ===
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

        # === 2. 严格参考你的方法获取内部 Chrome 内核 HWND ===
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

        # === 3. 获取坐标尺寸 ===
        rect = win32gui.GetWindowRect(main_h)
        x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]

        # === 4. 纯粹从寻找库拿句柄，web_overlay 不包含任何多余逻辑 ===
        if mode == "full":
            desktop_h = desktop_finder.get_mode_full_cover()
        elif mode == "wallpaper":
            desktop_h = desktop_finder.get_mode_wallpaper_only()
        else:
            desktop_h = desktop_finder.get_mode_below_icons()

        # === 5. 执行挂载 ===
        style = win32gui.GetWindowLong(chrome_h, win32con.GWL_STYLE)
        new_style = (style & ~win32con.WS_POPUP) | win32con.WS_CHILD
        win32gui.SetWindowLong(chrome_h, win32con.GWL_STYLE, new_style)

        win32gui.SetParent(chrome_h, desktop_h)
        win32gui.SetWindowPos(
            chrome_h, 0, x, y, w, h, win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW)

        # === 6. 隐藏外壳 ===
        win32gui.ShowWindow(main_h, win32con.SW_HIDE)
        ex_style = win32gui.GetWindowLong(main_h, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(main_h, win32con.GWL_EXSTYLE,
                               ex_style | win32con.WS_EX_TOOLWINDOW)

    threading.Thread(target=_detach, daemon=True).start()
