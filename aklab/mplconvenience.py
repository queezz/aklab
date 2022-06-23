"""
Convinience function for Matplotlib
"""
""" Matploblib adjustments
"""
import matplotlib.pylab as plt


def ticks_visual(ax, **kwarg):
    """
    makes auto minor and major ticks for matplotlib figure
    makes minor and major ticks thicker and longer
    """
    which = kwarg.get("which", "both")
    from matplotlib.ticker import AutoMinorLocator

    if which == "both" or which == "x":
        ax.xaxis.set_minor_locator(AutoMinorLocator())
    if which == "both" or which == "y":
        ax.yaxis.set_minor_locator(AutoMinorLocator())

    l1 = kwarg.get("l1", 7)
    l2 = kwarg.get("l2", 4)
    w1 = kwarg.get("w1", 1.0)
    w2 = kwarg.get("w2", 0.8)
    ax.xaxis.set_tick_params(width=w1, length=l1, which="major")
    ax.xaxis.set_tick_params(width=w2, length=l2, which="minor")
    ax.yaxis.set_tick_params(width=w1, length=l1, which="major")
    ax.yaxis.set_tick_params(width=w2, length=l2, which="minor")
    return


def grid_visual(ax, alpha=[0.1, 0.3]):
    """
    Sets grid on and adjusts the grid style.
    """
    ax.grid(which="minor", linestyle="-", alpha=alpha[0])
    ax.grid(which="major", linestyle="-", alpha=alpha[1])
    return


def gritix(**kws):
    """
    Automatically apply ticks_visual and grid_visual to the
    currently active pylab axes.
    """

    ticks_visual(plt.gca())
    grid_visual(plt.gca())
    return


def font_setup(size=13, weight="normal", family="serif", color="None"):
    """Set-up font for Matplotlib plots
    'family':'Times New Roman','weight':'heavy','size': 18
    """

    font = {"family": family, "weight": weight, "size": size}
    plt.rc("font", **font)
    plt.rcParams.update(
        {"mathtext.default": "regular", "figure.facecolor": color,}
    )


def ltexp(exp, decplace=1, short=False):
    """ converts 1e29 float to the scientific notation LaTeX string """
    import numpy as np

    exponent = int(np.floor(np.log10(abs(exp))))
    coeff = round(exp / np.float64(10 ** exponent), decplace)
    if not short:
        return f"{coeff}\\times 10^{{{exponent}}}"
    else:
        return f"10^{{{exponent}}}"


def font_ishihara(size=14):
    """ font and plot settings by Ishihara-kun"""
    font = {"family": "serif", "weight": "normal", "size": size}
    plt.rc("font", **font)
    plt.rcParams["xtick.direction"] = "in"  # x axis in
    plt.rcParams["ytick.direction"] = "in"  # y axis in
    plt.rcParams["axes.linewidth"] = 0.8  # axis line width
    plt.rcParams["axes.grid"] = False  # make grid


def ticks_ishihara():
    """ Ishihara's ticks """
    plt.tick_params(length=8, which="major")
    plt.tick_params(length=4, which="minor")


def reset_color_cycle():
    """ Reset color cycle """
    plt.gca().set_prop_cycle(None)


def set_size(width, fraction=1, subplots=(1, 1), ratio="golden"):
    """Set figure dimensions to avoid scaling in LaTeX.

    Parameters
    ----------
    width: float or string
            Document width in points, or string of predined document type
    fraction: float, optional
            Fraction of the width which you wish the figure to occupy
    subplots: array-like, optional
            The number of rows and columns of subplots.
    ratio: float or string.
            ratio = fig_hight_pt/fig_width_pt. If 'golden' equals to golden ratio
    Returns
    -------
    fig_dim: tuple
            Dimensions of figure in inches
    """
    if width == "thesis":
        width_pt = 426.79135
    elif width == "beamer":
        width_pt = 307.28987
    else:
        width_pt = width

    # Width of figure (in pts)
    fig_width_pt = width_pt * fraction
    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    # https://disq.us/p/2940ij3
    golden_ratio = (5 ** 0.5 - 1) / 2

    if ratio == "golden":
        ratio = golden_ratio

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * ratio * (subplots[0] / subplots[1])

    return (fig_width_in, fig_height_in)


def set_tick_size(ax, *size):
    """ Set matplotlib axis tick sizes
    For some reason the length from style is ignored.
    """
    width_major, length_major, width_minor, length_minor = size
    ax.xaxis.set_tick_params(width=width_major, length=length_major, which="major")
    ax.xaxis.set_tick_params(width=width_minor, length=length_minor, which="minor")
    ax.yaxis.set_tick_params(width=width_major, length=length_major, which="major")
    ax.yaxis.set_tick_params(width=width_minor, length=length_minor, which="minor")
