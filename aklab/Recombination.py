"""

"""
import matplotlib.pyplot as plt
import numpy as np
import aklab.mpls as akmp


class Recombination(object):
    """ Add docstring
    """

    def __init__(
        self,
        data,
        mass=2,
        p0=None,
        tag="",
        fit_range=None,
        jf=None,
        disp=True,
        tlim=1000,
        kd=5.1e-31,
        fix_jf=True,
        k1=8.286246100559756,
        k2=69.68,
        c1=3.0385593350848646e-07,
        style=False,
        yoffset=None,
    ):
        """
        TODO:
        Add docstring
        Kurokawa-kun, if you define a class with some default parameters, don't put a 
        list of arguments in the __init__ method. You can write a separate function to assign 
        the neccessary parameters, and call it when needed.
        Also for calculation, it's better to create a separate method and call it appropriatly.
        In the __init__ you just set-up the class.
        """
        self.target = "m" + str(mass)
        self.data = data[["tsec", self.target]].reset_index(drop=True)
        self.fix_jf = fix_jf
        self.kd = kd

        self.k1 = k1  # IG vs QMS
        self.k2 = k2  # Flux vs IG
        self.c1 = c1  # IG vs QMS constant

        if fit_range:
            if type(fit_range) == list:
                self.fit_data = self.data[
                    np.abs(np.array(self.data["tsec"]) - fit_range[0])
                    .argmin() : np.abs(np.array(self.data["tsec"]) - fit_range[1])
                    .argmin()
                ]
            else:
                self.fit_data = self.data[0 : np.abs(np.array(self.data["tsec"]) - fit_range).argmin()]
        else:
            self.fit_data = self.data

        self.fit_data["sub_sec"] = self.fit_data["tsec"] - self.fit_data.reset_index(drop=True)["tsec"][0]
        self.fit_data["flux"] = convert_itoj(self.fit_data[self.target], self.k1, self.k2, self.c1)

        self.ji = np.mean(self.fit_data["flux"][0:10])

        if jf:
            self.jf = convert_itoj(jf, self.k1, self.k2, self.c1)
        else:
            self.jf = np.mean(self.fit_data["flux"][-10:-1])
        self.t = np.array(self.fit_data["sub_sec"])
        self.y = np.array(self.fit_data["flux"])
        self.tag = tag
        if fix_jf:
            self.p0 = p0
            self.param, self.cov = self.fitting(self.fitting_function, self.t, self.y)
        else:
            if type(p0) == list:
                self.p0 = p0[0]
            else:
                self.p0 = p0
            self.param, self.cov = self.fitting(self.fitting_function2, self.t, self.y)

        if disp:
            fig = plt.figure(figsize=(16, 9), dpi=50, facecolor="white")
            self.ax = fig.add_subplot(111)
            l1 = self.plot(self.t, self.y, label="data", scatter=True, fig=False, convert=False, color="k")
            if fix_jf:
                l2 = self.plot(
                    np.linspace(0, tlim, tlim * 100),
                    self.fitting_function(np.linspace(0, tlim, tlim * 100), self.param[0], self.param[1]),
                    label="fitting",
                    color="r",
                    fig=False,
                    convert=False,
                )
            else:
                l2 = self.plot(
                    np.linspace(0, tlim, tlim * 100),
                    self.fitting_function2(np.linspace(0, tlim, tlim * 100), self.param[0]),
                    label="fitting",
                    color="r",
                    fig=False,
                    convert=False,
                )
            if style:
                a = r"${\rm J}{\ }{\rm (\times 10^"
                b = f"{yoffset}"
                c = r"m^{-2}s^{-1})}$"
                self.ax.set_ylabel(a + b + c)
                self.ax.yaxis.offsetText.set_fontsize(0)
        self.ku = self.calc_ku(self.param, disp)

    def fitting_function(self, t, a, b):
        """
        Add docstring
        """
        at = (
            np.exp(t * a)
            * (np.sqrt(self.jf + b) + np.sqrt(self.ji))
            / (np.sqrt(self.jf + b) - np.sqrt(self.ji))
        )
        jt = (self.jf + b) * ((at - 1) / (at + 1)) ** 2
        return jt

    def fitting_function2(self, t, a):
        """ Add docstring
        """
        at = np.exp(t * a) * (np.sqrt(self.jf) + np.sqrt(self.ji)) / (np.sqrt(self.jf) - np.sqrt(self.ji))
        jt = (self.jf) * ((at - 1) / (at + 1)) ** 2
        return jt

    def fitting(self, func, t, y):
        """
        Add docstring
        """
        from scipy.optimize import curve_fit

        return curve_fit(func, t, y, p0=self.p0, maxfev=10000)

    def calc_ku(self, param, disp, l=20e-3):  # l:membrane thickness
        """ Add docstring
        """
        la = param[0]
        if self.fix_jf:
            self.jf += param[1]
        self.sum_k = la * l / (2 * np.sqrt(self.jf))
        ku = self.sum_k * np.sqrt(self.kd) - self.kd
        if disp:
            print(f"ku = {ku} m^4 s^-1 {self.tag}")
        return ku

    def calc_loop(self, tlim=1000, loop=1000, p0=None, style=False, xoffset=None, yoffset=None):
        """ Add docstring
        """
        from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

        t = np.linspace(0, tlim)
        x = np.linspace(1, loop, loop)
        jf_list = []
        ku_list = []
        if p0:
            self.p0 = p0

        for i in range(loop):
            if self.fix_jf:
                self.param, self.cov = self.fitting(self.fitting_function, self.t, self.y)
                self.jf += self.param[1]
            else:
                self.param, self.cov = self.fitting(self.fitting_function2, self.t, self.y)
            self.p0 = self.param
            ku_list.append(self.calc_ku(self.param, disp=False))
            jf_list.append(self.jf)

        if self.fix_jf:
            y = np.array(self.fitting_function(t, self.param[0], self.param[1]))
        else:
            y = np.array(self.fitting_function2(t, self.param[0]))
        self.st_ku = np.mean(ku_list[int(-loop / 5) : -1])
        self.st_jf = np.mean(jf_list[int(-loop / 5) : -1])

        figure = plt.figure(figsize=(24, 8))
        gs_master = GridSpec(nrows=2, ncols=2, height_ratios=[1, 1])

        gs_1 = GridSpecFromSubplotSpec(nrows=2, ncols=1, subplot_spec=gs_master[0:2, 0])
        axes_1 = figure.add_subplot(gs_1[:, :])

        gs_2_and_3 = GridSpecFromSubplotSpec(nrows=2, ncols=1, subplot_spec=gs_master[0:2, 1])
        axes_2 = figure.add_subplot(gs_2_and_3[0, :])
        axes_3 = figure.add_subplot(gs_2_and_3[1, :])

        axes_1.plot(t, y, label="fit", color="r")
        axes_1.scatter(self.t, self.y, label="data", color="b")
        axes_2.plot(x, jf_list)
        axes_3.plot(x, ku_list)
        axes_1.set_xlabel(r"${\rm Time}{\ }{\rm (s)}$")
        if style:
            a = r"${\rm J}{\ }({\times}10^{"
            b = f"{yoffset}"
            c = r"}{\ }m^{-2}s^{-1})}$"
            axes_1.set_ylabel(a + b + c)
            axes_1.yaxis.offsetText.set_fontsize(0)
            axes_1.set_ylim(0, max(y) * 1.2)
        else:
            axes_1.set_ylabel(r"${\rm J{\ }(m^{-2}s^{-1})}$")
        axes_2.set_ylabel(r"${J_f}$")
        axes_3.set_xlabel("Number of trials")
        axes_3.set_ylabel(r"${ku}$")
        axes_1.legend()

        akmp.ticks_visual(axes_1)
        akmp.grid_visual(axes_1)
        plt.tight_layout
        print(f"steady value Jf is {self.jf}")
        print(f"ku = {self.st_ku}")
        return self.st_jf, self.st_ku

    def plot(
        self,
        x,
        y,
        label="",
        title=None,
        scatter=False,
        color=None,
        fig=True,
        convert=True,
        co=[8.733935665396627, 69.68, 2.978590280897269e-07],
        subtract=False,
    ):
        """ Add docstring
        """
        akmp.font_setup(size=28)
        if fig:
            fig = plt.figure(figsize=(16, 9), dpi=50)
            self.ax = fig.add_subplot(111)
        if convert:
            y = convert_itoj(y, co[0], co[1], co[2])
            self.ax.set_ylabel(r"${\rm J}{\ }{\rm (m^{-2}s^{-1})}$")
        else:
            self.ax.set_ylabel(r"${\rm J}{\ }{\rm (m^{-2}s^{-1})}$")
        self.ax.set_xlabel(r"${\rm Time}{\ }{\rm (s)}$")
        if subtract:
            self.ax.set_ylabel(r"${\rm {\Delta}J}{\ }{\rm (m^{-2}s^{-1})}$")
        y = y - min(y)
        if scatter:
            self.ax.scatter(x, y, label=label, color=color, s=10)
        else:
            self.ax.plot(x, y, label=label, color=color)
        self.ax.legend()
        if title:
            self.ax.set_title(title)
        akmp.ticks_visual(self.ax)
        akmp.grid_visual(self.ax)


def convert_itoj(i, k1=8.73, k2=69.68, c1=2.97e-07):
    """ Add description

    Parameters
    ----------
    i: float
    k1: float
    k2: float
    c1: float
    """
    from scipy.constants import Avogadro

    membrane_area = 0.0015
    return 2 * Avogadro * (i * k1 + c1) / (k2 * membrane_area)


def disp_table(df, index=None, save=False, dpi=100, figsize=None, fontsize=28, titlefontname=None):
    """ Add description

    Parameters
    ----------
    df: pandas.DataFrame
    index: None
    save: bool
    dpi: int
    figsize: None 
    fontsize: int
    titlefontname: string
    """
    if not figsize:
        figsize = ((len(df.columns) + 1) * 1.2, (len(df) + 1) * 0.4)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.axis("off")
    akmp.font_setup(size=fontsize)
    if index:
        tbl = ax.table(cellText=df.values, bbox=[0, 0, 1, 1], colLabels=df.columns, rowLabels=index)
    else:
        tbl = ax.table(cellText=df.values, bbox=[0, 0, 1, 1], colLabels=df.columns,)

    if save:
        plt.savefig("table.png")  # PNG画像出力

    if titlefontname:
        plt.rcParams["fontname"] = titlefontname
    plt.show()

