"""
Signal processing tools: filter, smooth, etc.
"""

import numpy as np


def fft_filtering(sample, dt, fc):
    """ Lowpass filter

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
