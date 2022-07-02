"""
Signal processing tools: filter, smooth, etc.
"""

import numpy as np


def fft_filtering(sample, dt, fc):
    """ Lowpass filter
    *TODO*: calculate sampling time with numpy.gradient, no need to manually suply it

    Parameters
    ----------
    sample: array-like
        signal
    dt: float
        sampling interval
    fc: float
        upper frequency limit

    Returns
    -------
    g: np.array
        filtered signal
    """
    # ローパスフィルタ
    N = len(sample)  # サンプル数
    # dt is サンプリング間隔
    t = np.arange(0, N * dt, dt)  # 時間軸
    freq = np.linspace(0, 1.0 / dt, N)  # 周波数軸

    # fc = 0.1        # カットオフ周波数
    fs = 1 / dt  # サンプリング周波数
    # fm = (1/2) * fs # アンチエリアジング周波数
    fc_upper = fs - fc  # 上側のカットオフ　fc～fc_upperの部分をカット

    # 元波形をfft
    F = np.fft.fft(sample)

    # 元波形をコピーする
    G = F.copy()

    # ローパス
    G[((freq > fc) & (freq < fc_upper))] = 0 + 0j

    # 高速逆フーリエ変換
    g = np.fft.ifft(G)

    # 実部の値のみ取り出し
    return np.array(g.real)


def poly_smooth(x, y, order, n=1):
    """
    Fit data with a polinomial and return interpolated signal

    Parameters
    ----------
    x: list or np.array
    y: list or np.array
    order: int
        order of the polinomial
    n: int
        multiplier of the number of data points
    
    Returns
    -------
    tuple
        interpolated x,y
    """
    x = np.array(x)
    y = np.array(y)
    xs = np.linspace(x.min(), x.max(), len(x) * n)
    fit = np.polyfit(x, y, order)
    fit_fn = np.poly1d(fit)
    return xs, fit_fn(xs)


def bspline(cv, n=100, degree=3, periodic=False):
    """
    Calculate n samples on a bspline

    Parameters
    ----------
    cv: list or np.array()     
        Array of control vertices
    n: int
        Number of samples to return
    degree:
       Curve degree
    periodic: bool
        True - Curve is closed, False - Curve is open
    """
    import scipy.interpolate as si

    # If periodic, extend the point array by count+degree+1
    cv = np.asarray(cv)
    count = len(cv)

    if periodic:
        factor, fraction = divmod(count + degree + 1, count)
        cv = np.concatenate((cv,) * factor + (cv[:fraction],))
        count = len(cv)
        degree = np.clip(degree, 1, degree)

    # If opened, prevent degree from exceeding count-1
    else:
        degree = np.clip(degree, 1, count - 1)

    # Calculate knot vector
    kv = None
    if periodic:
        kv = np.arange(0 - degree, count + degree + degree - 1)
    else:
        kv = np.clip(np.arange(count + degree + 1) - degree, 0, count - degree)

    # Calculate query range
    u = np.linspace(periodic, (count - degree), n)

    # Calculate result
    return np.array(si.splev(u, (kv, cv.T, degree))).T


def index_of_nearest(signal, value):
    """ 
    Index of the nearest value in an array

    Parameters
    ----------
    signal: array
    value: float

    Returns
    -------
    int
        index of the nearest value in the signal

    """
    signal = np.array(signal)
    return (np.abs(signal - value)).argmin()
