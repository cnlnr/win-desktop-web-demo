from web_overlay import overlay
import webview


if __name__ == '__main__':
    window = webview.create_window(
        'Desktop Example', 'index.html', fullscreen=True)
    webview.start(overlay, window)
