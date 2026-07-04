import webview
from web_overlay import overlay

if __name__ == '__main__':
    window = webview.create_window(
        'Desktop Example',
        r'https://cnlnr.github.io/TimePlot/four-ring-clock.html',
        fullscreen=True
    )

# 透明背景加这个参数
# transparent=True

    # 模式二选一：
    # mode='full'      -> 全覆盖（网页把桌面图标遮挡，网页可以正常点击交互）
    # mode='wallpaper' -> 当成壁纸（桌面图标在最上方，网页作为背景不能被鼠标点击操作）

    webview.start(lambda w: overlay(w, mode='wallpaper'), window)
