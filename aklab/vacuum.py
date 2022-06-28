"""
Tools for vacuum calculations: QMS vs IG calibration, etc.
"""
import numpy as np
import aklab.mpls as akmp


def qms_ig_calibration(
    raspi, qms, rangeis, gain=1, show_summary=False, mass_select="2", style=False, xoffset=None, yoffset=None
):
    """
    QMS vs IG calibration

    Parameters
    ----------
    raspi: raspi.raspi
        plasma control unit data class
    qms: `qulee.QMS`
        QMS class with calibration data
    rangeis: list-like
        time interval [start,end], datetime.datetime
    show_summary: bool
        show summary
    mass_select: string
        "2"
    style: bool
        plot style, one of two
    xoffset: None or float
        offset
    yoffset: None or float
        offset
    """
    import matplotlib.pylab as plt

    mass = "m" + mass_select

    a = rangeis[0].strftime("%Y%m%d%H%M%S")
    b = rangeis[1].strftime("%Y%m%d%H%M%S")
    raspi_calib = raspi.adc.query(f"{a} < date < {b}").reset_index(drop=True)[["date", "time", "pd"]]
    qms_calib = qms.data.query(f"{a} < date < {b}").reset_index(drop=True)[[mass, "tsec"]]
    fitting_time = raspi_calib["date"][len(raspi_calib) - 1] - raspi_calib["date"][0]

    num_raspi = len(raspi_calib)
    num_qms = len(qms_calib)
    num_interpolation = num_raspi - num_qms
    dense = num_interpolation / (num_qms - 1)

    """m2のデータを線形補完"""
    a = []  # 補完の区切りを作成
    j = 1
    for i in range(num_interpolation):
        if i > j * dense:
            a += [i - 1]
            j += 1

    a += [num_interpolation]

    j = 0  # 各区間に何個の補完を行うか
    b = []
    for i in a:
        b += [i - j]
        j = i

    c = []  # 線形補完
    for i in range(len(b)):
        c += [qms_calib[mass][i]]
        d = (qms_calib[mass][i + 1] - qms_calib[mass][i]) / (b[i] + 1)
        for j in range(b[i]):
            c += [qms_calib[mass][i] + d * (j + 1)]

    c += [qms_calib[mass][len(qms_calib) - 1]]

    import statsmodels.api as sm

    x = c
    y = np.array(raspi_calib["pd"]) * gain
    mod = sm.OLS(y, sm.add_constant(x))
    res = mod.fit()
    c1 = res.params[0]
    k1 = res.params[1]
    h = []
    for i in range(len(x)):
        h += [x[i] * k1]

    if show_summary:
        print(res.summary())

    print(f"{fitting_time}秒間のデータを利用")

    print(f"Proportional constant P/current is {k1}")

    akmp.font_setup(size=28)

    if style:
        if xoffset and yoffset:
            fig = plt.figure(figsize=(16, 9), dpi=50)
            a = r"$p_{\rm ig}$ $({\rm {\times}10^{"
            b = f"{yoffset}"
            c = r"}{\ }Torr})$"
            d = r"$I{\ }({\rm {\times}10^{"
            e = f"{xoffset}"
            f = r"}{\ }A})$"
            ax = fig.add_subplot(1, 1, 1, xlabel=(d + e + f), ylabel=(a + b + c))
            ax.xaxis.offsetText.set_fontsize(0)
            ax.yaxis.offsetText.set_fontsize(0)
            l1 = [ax.scatter(x, y, label="QMSsignal-IG", c="k")]
            l2 = ax.plot(x, c1 + h, label="Fitting", c="r")
            ax.legend(handles=l1 + l2, labels=["Data", "Fitting"])
            akmp.ticks_visual(ax)
            akmp.grid_visual(ax)
            ax.set_ylim(0, max(y) * 1.1)
            ax.set_xlim(right=2.25e-7)
            ax.set_xticks([i for i in np.linspace(0, 2.25e-7, 10)])
            return k1, c1

        else:
            print("input offset!")
            return False, False
    else:
        fig = plt.figure(figsize=(16, 9), dpi=50)
        ax = fig.add_subplot(1, 1, 1, xlabel="QMS Current [A]", ylabel=r"$P_{\rm per}$ [Torr]")
        ax.scatter(x, y, label="QMSsignal-IG")
        ax.plot(x, c1 + h, label="Fitting")
        ax.legend(bbox_to_anchor=(1, 1), loc="upper right", borderaxespad=0, fontsize=28)
        akmp.ticks_visual(ax)
        akmp.grid_visual(ax)
        return k1, c1
