import win32con
import win32gui


def _trigger_workerw():
    """向大总管发送分层信号，确保拆分出壁纸层"""
    progman = win32gui.FindWindow("Progman", "Program Manager")
    win32gui.SendMessageTimeout(
        progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)
    return progman


def get_mode_full_cover():
    """模式1：全覆盖（挂载在大总管 Progman 上，网页可完美交互）"""
    return _trigger_workerw()


def get_mode_wallpaper_only():
    """模式2：当成壁纸（精准匹配你 Spy++ 图中的 Window WorkerW）"""
    progman = _trigger_workerw()

    # 【核心修正】：不要再去 Enum 全局窗口盲猜了！
    # 直接根据你的 Spy++ 图，去 Progman (Program Manager) 内部寻找类名为 "WorkerW" 的直接子窗口。
    # 并且传入标题为 "" (空字符串)，这能 100% 精准咬住你图里那个 002D083A 的 WorkerW。
    worker_w = win32gui.FindWindowEx(progman, 0, "WorkerW", "")

    # 如果系统尚未彻底生成此 WorkerW，则用大总管 Progman 兜底，确保网页绝对不会隐形
    return worker_w if worker_w else progman
