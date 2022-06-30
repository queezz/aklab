"""
Tools to work with files and folders, uses :code:`os`, :code:`shutil`.
"""
import os


def copy(src, targ, key, copy=False):
    """
    Copy files

    Parameters:
    -----------
    scrs: string
        source directory
    targ: string
        target directory
    key: str
        search for key in :func:`os.listdir(src)`
    copy: bool
        default False, if True - will copy

    Returns:
    --------
    list or None
        if no exception, will return list of matching filenames
    """
    try:
        ls = os.listdir(src)
        ls = [i for i in ls if key in i]
        srcls = [os.path.join(src, i) for i in ls]
        targls = [os.path.abspath(os.path.join(targ, i)) for i in ls]

        if copy:
            import shutil

            [shutil.copy(i, j) for i, j in zip(srcls, targls)]

        return ls

    except Exception as e:
        print(f"{e}")

