Module aklab.mpls
=================
Convinience function for Matplotlib

Functions
---------

    
`font_ishihara(size=14)`
:   font and plot settings by Ishihara-kun

    
`font_setup(size=13, weight='normal', family='serif', color='None')`
:   Set-up font for Matplotlib plots
    'family':'Times New Roman','weight':'heavy','size': 18

    
`grid_visual(ax, alpha=[0.1, 0.3])`
:   Sets grid on and adjusts the grid style.

    
`gritix(**kws)`
:   Automatically apply ticks_visual and grid_visual to the
    currently active pylab axes.

    
`ltexp(exp, decplace=1, short=False)`
:   converts 1e29 float to the scientific notation LaTeX string

    
`reset_color_cycle()`
:   Reset color cycle

    
`set_size(width, fraction=1, subplots=(1, 1), ratio='golden')`
:   Set figure dimensions to avoid scaling in LaTeX.
    
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

    
`set_tick_size(ax, *size)`
:   Set matplotlib axis tick sizes
    For some reason the length from style is ignored.

    
`ticks_ishihara()`
:   Ishihara's ticks

    
`ticks_visual(ax, **kwarg)`
:   makes auto minor and major ticks for matplotlib figure
    makes minor and major ticks thicker and longer