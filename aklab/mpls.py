"""
Convinience function for Matplotlib
"""

import matplotlib.pylab as plt
import numpy as np


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
     :math:`1.23e31 \\rightarrow  1.23\\times 10^{31}`    
   
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


def figprep(width=246, subplots=[1, 1], dpi=100, **kws):
    """
    Create matplotlib figure with given width in points
    
    Parameters
    ----------
    width: float
        figure width in points
    subplots: aray-like
            [1,1] by default. The number of rows and columns.
    dpi: int
        figure dpi, useflu to adjust JupyterLab figure size

    Returns
    -------
    tuple
            (fig, axs), matplotlib.pylab.subplots
    """
    return plt.subplots(subplots[0], subplots[1], figsize=set_size(width, **kws), dpi=dpi)


def polygon(n=6):
    """
    Calculate vertices for an n-gone, inscirbed in a unit circle.
    First vertice at 1.
    """
    t = np.arange(0, np.pi * 2 * (n + 1) / n, 2 * np.pi / n)
    return (np.cos(t), np.sin(t))


def vec(a, b, **kws):
    """
    Draw a vector from point a to point b. Uses complex numbers.

    Parameters
    ----------
    a,b: complex
        start and end for the vector.
    kws: dict
        keyword arguments for matplotlib.pyplot.plot
    """
    plt.plot([a.real, b.real], [a.imag, b.imag], "-", **kws)


def plot_circ(r=1, o=0 + 0j, **kws):
    """
    Plot a circle.

    Parameters
    ----------
    r: float
        radius
    o: complex
        origin
    kws: dict
        keyword arguments for matplotlib.pyplot.plot
    """
    cx, cy = polygon(100)
    c = kws.get("c", "k")
    ls = kws.get("ls", "-")
    for i in ["c", "ls"]:
        try:
            kws.pop(i)
        except:
            pass
    plt.plot(cx * r + o.real, cy * r + o.imag, c=c, ls=ls, **kws)


def multiple_formatter(denominator=2, number=np.pi, latex="\pi"):
    """
    Formatter with letters, multiple of pi
    """

    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    def _multiple_formatter(x, pos):
        den = denominator
        num = int(np.rint(den * x / number))
        com = gcd(num, den)
        (num, den) = (int(num / com), int(den / com))
        if den == 1:
            if num == 0:
                return r"$0$"
            if num == 1:
                return r"$%s$" % latex
            elif num == -1:
                return r"$-%s$" % latex
            else:
                return r"$%s%s$" % (num, latex)
        else:
            mm = ""
            if num < 0:
                mm = "-"
            if num == 1:
                return r"$\frac{%s}{%s}$" % (latex, den)
            elif num == -1:
                return f"${mm}\\frac{{{latex}}}{{{den}}}$"
            else:
                return f"${mm}\\frac{{{abs(num)}}}{{{den}}}{latex}$"

    return _multiple_formatter


class Multiple:
    """
    Matplotlib formatter
    """

    def __init__(self, denominator=2, number=np.pi, latex="\pi"):
        self.denominator = denominator
        self.number = number
        self.latex = latex

    def locator(self):
        return plt.MultipleLocator(self.number / self.denominator)

    def formatter(self):
        return plt.FuncFormatter(multiple_formatter(self.denominator, self.number, self.latex))


# Drawing examples


def hand(minute, hours=0, l=2, o=0, angle=np.pi / 48, hour=False, **kws):
    """
    Draw clock hand
    """
    phi = np.pi / 2 - np.pi / 30 * minute
    if hour:
        phi = np.pi / 2 - np.pi * (1 / 6 * hours + 1 / 360 * minute)
        angle = np.pi / 24
    ab = l * np.exp(1j * (phi))
    a = ab / np.cos(angle) / 2 * np.exp(1j * angle)
    b = ab / np.cos(angle) / 2 * np.exp(-1j * angle)
    c = kws.get("c", "k")
    vec(o, a + o, c=c)
    vec(o, b + o, c=c)
    vec(a + o, o + a + b, c=c)
    vec(b + o, a + b + o, c=c)


def plot_clock_face(r=2, o=0, fontsize=10):
    """
    Plot clock face
    """
    gs = [r * np.exp(1j * (-np.pi / 6 + np.pi / 2 - np.pi / 6 * i)) for i in range(12)]
    ms = [r * np.exp(1j * (np.pi / 30 * i)) for i in range(60)]
    plot_circ(r, o=o)
    [vec(o + g * 1.05, o + g * 1.1, c="C3") for g in ms]
    [vec(o + g, o + g * 1.15, c="C2", lw=1.5) for g in gs]

    ax = plt.gca()
    [
        ax.text((o + p * 1.25).real, (o + p * 1.25).imag, t + 1, va="center", ha="center", fontsize=fontsize)
        for t, p in enumerate(gs)
    ]


def show_analog_time(hours, minutes, r=2, c="C0", o=0, fontsize=10):
    """
    Draw a clock with two hands
    """

    plot_clock_face(r, o=o, fontsize=fontsize)
    hand(minutes, hours, l=r * 0.9, hour=True, c=c, o=o)
    hand(minutes, l=r * 0.95, c=c, o=o)

    plt.axis("off")
    plt.gcf().set_dpi(200)
    plt.gca().set_aspect("equal")

