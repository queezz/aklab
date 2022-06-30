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
        targls = [os.path.abspath(os.path.join(targ, add_sufix(i, suffix=suffix))) for i in ls]

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

