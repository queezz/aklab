"""
Tools for reading a binary file
"""


def _to_string(c):
    """ convert bytes to string. c: string or bytes"""
    return c if not isinstance(c, bytes) else c.decode("utf-8")


def _read_string(fp, length=None):
    """Read a string of the given length. If no length is provided, the
    length is read from the file."""
    if length is None:
        length = int(_to_string(fp.readline()))
    return fp.read(length)


def _read_until(fp, terminator=" "):
    """Read a space-delimited word."""
    word = ""
    while True:
        c = _to_string(fp.read(1))
        if c == terminator or c == "\n":
            if len(word) > 0:
                break
        word += c
    return word


def _read_int(fp):
    return int(_read_until(fp, " "))


def _read_float(fp):
    return float(_read_until(fp, " "))

