.. _matplotlibs:

=====================================================
Matplotlib tools
=====================================================

Examples
--------
.. jupyter-execute::

    import matplotlib.pyplot as plt
    from aklab import mpls as akmp

    akmp.font_setup(size=14)
    fig, axs = plt.subplots(3, 1)
    fig.set_size_inches(akmp.set_size(500, ratio=1))
    plt.subplots_adjust(top=0.99, bottom=0.01, hspace=0.3, wspace=0.1)

    akmp.ticks_visual(axs[0])
    akmp.grid_visual(axs[1])
    txt = f"$x={akmp.ltexp(1.23e29)}$"
    axs[2].text(0.5, 0.5, txt,transform=axs[2].transAxes, ha="center")

.. jupyter-execute::

    akmp.figprep(subplots=[3,1],dpi=60)

:func:`~aklab.mpls.gritix` combines :func:`~aklab.mpls.ticks_visual` and :func:`~aklab.mpls.grid_visual`.

