"""
Tools to work with files and folders, uses :code:`os`, :code:`shutil`.
"""
import os


def copy(src, targ, keys, suffix="", copy=False):
    """
    Copy files

    Parameters
    -----------
    scrs: string
        source directory
    targ: string
        target directory
    keys: list
        list of keys. If all keys are in filename in :func:`os.listdir(src)`, adds to list
    copy: bool
        default False, if True - will copy

    Returns
    --------
    list or None
        if no exception, will return list of matching filenames
    """
    try:
        ls = os.listdir(src)
        for key in keys:
            ls = [i for i in ls if key in i]

        srcls = [os.path.join(src, i) for i in ls]
        targls = [
            os.path.abspath(os.path.join(targ, add_sufix(i, suffix=suffix))) for i in ls
        ]

        if copy:
            import shutil

            [shutil.copy(i, j) for i, j in zip(srcls, targls)]

        return ls, srcls, targls

    except Exception as e:
        print(f"{e}")


def add_sufix(pth, suffix=""):
    """
    Add suffix to filepath

    Parameters
    ----------
    pth: str
        file path
    suffix: str
        suffix to append before file extension

    Returns
    -------
    str
        path with appended suffix 
    """
    c = os.path.splitext(pth)
    return f"{c[0]}{suffix}{c[1]}"


def docs(n=5):
    """
    On Windows and Mac, returns Documents or Desktop folder

    Parameters
    ----------
    n: int
        n = 0 - Desktop
        n = 5 - Documents
        n = 40 - Current User folder
    """
    import platform

    if platform.system() == "Windows":
        import ctypes.wintypes

    sfx = {0: "Desktop", 5: "Documents", 40: ""}
    if platform.system() == "Windows":
        CSIDL_PERSONAL = n  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Want current, not default value
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(
            0, CSIDL_PERSONAL, 0, SHGFP_TYPE_CURRENT, buf
        )
        return buf.value

    elif platform.system() == "Darwin":
        return os.path.join(os.path.expanduser("~"), sfx[n])

    elif platform.system() == "Linux":
        return os.path.join(os.path.expanduser("~"), sfx[n])


def platf():
    """
    Returns
    -------
    string
        OS name
    """
    import platform

    if platform.system() == "Windows":
        return "win"
    elif platform.system() == "Darwin":
        return "os x"
    elif platform.system() == "Linux":
        return "linux"
