import webview
from web_overlay import overlay

if __name__ == '__main__':
    # 1. 创建你的 Web 窗口（开启全屏以铺满桌面）
    window = webview.create_window(
        'Desktop Wallpaper',
        'https://www.bing.com',  # 或者是你的本地 HTML 文件/网页地址
        fullscreen=True
    )

    # 2. 启动程序，并选择你需要的挂载模式：
    #
    # 模式 A: 'full'       -> 全覆盖到桌面，网页把快捷方式图标也挡住
    # 模式 B: 'below_icon' -> 网页挂在快捷方式图标下方，图标可见且网页可正常操作
    # 模式 C: 'wallpaper'  -> 网页完全融入最底层壁纸，图标可见且网页不可操作（鼠标穿透）
    #
    # 只需要在这里修改对应的字符串参数即可：
    webview.start(lambda w: overlay(w, mode='full'), window)
