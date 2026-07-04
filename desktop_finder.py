import win32con
import win32gui


def _get_progman_and_trigger():
    """找到 Program Manager 并触发 0x052C 确保层级处于激活状态"""
    progman = win32gui.FindWindow("Progman", "Program Manager")
    win32gui.SendMessageTimeout(
        progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)
    return progman


def get_mode_full_cover():
    """模式1：全覆盖（直接挂在大总管 Progman 上，遮挡所有人）"""
    return _get_progman_and_trigger()


def get_mode_below_icons():
    """模式2：图标下方（深度挂载到 FolderView / SysListView32 内部）"""
    progman = _get_progman_and_trigger()

    # 第一层：依图寻找大外壳 SHELLDLL_DefView
    shell_def = win32gui.FindWindowEx(progman, 0, "SHELLDLL_DefView", None)

    # 第二层：精准挖出你要的名称为 "FolderView"，类名为 "SysListView32" 的窗口
    folder_view = win32gui.FindWindowEx(
        shell_def, 0, "SysListView32", "FolderView")

    # 如果找到了，直接把这个图标层作为网页的父级返回
    return folder_view if folder_view else shell_def


def get_mode_wallpaper_only():
    """模式3：纯壁纸（挂载到与 SHELLDLL_DefView 同级的隐藏 WorkerW 上）"""
    progman = _get_progman_and_trigger()

    # 按照图中所示，寻找 Progman 下面那个类名为 WorkerW 且标题为空的窗口
    worker_w = win32gui.FindWindowEx(progman, 0, "WorkerW", "")

    return worker_w if worker_w else progman
