"""
Convinience function for Matplotlib
"""

import matplotlib.pylab as plt


def ticks_visual(ax, size=[7, 4, 1, 0.8], which="both"):
    """
    Makes auto minor and major ticks for matplotlib figure and adjusts ticks sizes.

    Parameters
    ----------
    ax: matplotlib.pylab.axes
        axes
    size: array-like
        size = [l1,l2,w1,w2] length and width for major (1) and minor (2) ticks
    which: string
        which = ['x'| 'y' | 'both'] - set auto minor locator
    """
    from matplotlib.ticker import AutoMinorLocator

    if which == "both" or which == "x":
        ax.xaxis.set_minor_locator(AutoMinorLocator())
    if which == "both" or which == "y":
        ax.yaxis.set_minor_locator(AutoMinorLocator())

    l1, l2, w1, w2 = size

    ax.xaxis.set_tick_params(width=w1, length=l1, which="major")
    ax.xaxis.set_tick_params(width=w2, length=l2, which="minor")
    ax.yaxis.set_tick_params(width=w1, length=l1, which="major")
    ax.yaxis.set_tick_params(width=w2, length=l2, which="minor")


def grid_visual(ax, alpha=[0.1, 0.3]):
    """
    Sets grid on and adjusts the grid style.
    
    Parameters
    ----------
    ax: matplotlib.pylab.axes
        Axes where the grid will be displayed.
    alpha: array-like
        alpha = [minor alpha, major alpha] - transparancy of grid lines 
    """
    ax.grid(which="minor", linestyle="-", alpha=alpha[0])
    ax.grid(which="major", linestyle="-", alpha=alpha[1])
    return


def gritix(**kws):
    """
    Apply `ticks_visual` and `grid_visual` to the active pylab axes.
    """

    ticks_visual(plt.gca())
    grid_visual(plt.gca())
    return


def font_setup(size=13, weight="normal", family="serif", color="None", fontname="Sans"):
    """Set-up font for matplotlib using rc, see https://matplotlib.org/stable/tutorials/text/text_props.html
    specific for `family` fontnames: ['Sans' | 'Courier' | 'Helvetica' ...]

    Parameters
    ----------
    family: string
        [ 'serif' | 'sans-serif' | 'cursive' | 'fantasy' | 'monospace' ]
    weight: string
        [ 'normal' | 'bold' | 'heavy' | 'light' | 'ultrabold' | 'ultralight']
    size: float
         18 by default
    color: string
        any matplotlib color    
    """

    font = {"family": family, "weight": weight, "size": size}
    plt.rc("font", **font)
    plt.rcParams.update(
        {"mathtext.default": "regular", "figure.facecolor": color,}
    )


def ltexp(val, decplace=1, short=False):
    """ Converts float to the scientific notation LaTeX string,
     \\( :math: `1.23e31 \\rightarrow  1.23\\times 10^{31}` \\)
     :math: `\\frac{x^2}{i^3}`   

    Parameters
    ----------
    val: float
        number to convert
    decplace: int
        number of decimal places to display in the pre-exponent
    short: bool
        if True, only shows exponent part 
    """
    import numpy as np

    exponent = int(np.floor(np.log10(abs(val))))
    coeff = round(val / np.float64(10 ** exponent), decplace)
    if not short:
        return f"{coeff}\\times 10^{{{exponent}}}"
    else:
        return f"10^{{{exponent}}}"


def font_ishihara(size=14):
    """ font and tick settings used by Ishihara-kun"""
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


def set_tick_size(ax, size):
    """ Set matplotlib axis tick sizes
    For some reason the length from style is ignored.

    Parameters
    ----------
    ax: matplotlib.pylab.axes
        axes for adjustment
    size: array-like
        size = [width_major, length_major, width_minor, length_minor]
    """
    width_major, length_major, width_minor, length_minor = size
    ax.xaxis.set_tick_params(width=width_major, length=length_major, which="major")
    ax.xaxis.set_tick_params(width=width_minor, length=length_minor, which="minor")
    ax.yaxis.set_tick_params(width=width_major, length=length_major, which="major")
    ax.yaxis.set_tick_params(width=width_minor, length=length_minor, which="minor")


def figprep(width=246, **kws):
    """ Create matplotlib figure with given width in points
    
    Parameters
    ----------
    width: float
        figure width in points

    Keyword Arguments for aklab.mpls.set_size
    -----------------
    subplots: aray-like
            The number of rows and columns
    ratio: float or string
            ratio=fig_hight_pt/fig_width_pt

    Returns
    -------
    (fig, axs): tuple
            matplotlib.pylab.subplots
    """
    subplots = kws.get("subplots", [1, 1])
    return plt.subplots(subplots[0], subplots[1], figsize=set_size(width, **kws), dpi=200)


def figprep(width=246, dpi=200, **kws):
    """ Create matplotlib figure with given width in points
    for `kws` see `set_size`
    
    Parameters
    ----------
    width: float
        figure width in points
    dpi: float
        figure dpi, use to increase displayed figure in a notebook

    Returns
    -------
    subplots: tuple
            (fig, axs), a matplotlib.pylab.subplots
    """
    subplots = kws.get("subplots", [1, 1])
    return plt.subplots(subplots[0], subplots[1], figsize=set_size(width, **kws), dpi=dpi)

