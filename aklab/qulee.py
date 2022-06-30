"""
"Qulee" (pronounced as "KLEE"), is ULVAC's latest model for residual gas analysis. 

Tools to work with Qulee mass spectrometer outputs (CSV) and maybe later with Qulee software?
Created 2021/06/11 by queezz
"""
from aklab.constants import *


class QMS:
    """
    Read Qulee QMS CSV file, generate pandas.DataFrame, plot data.
    
    Parameters
    ----------
    datapath: string
            path to converted to csv format Qulee QMS data.
    """

    def __init__(self, datapath):
        """ """
        self.data = None
        self.path = datapath
        self.qms_file_parser()
        self.load_data()
        self.clr = generate_colors(self.masslist)

    def qms_file_parser(self):
        """ 
        Parses the QMS csv file header.
        """
        import codecs
        import datetime

        channels = []
        mlist = []
        params = dict([])
        with codecs.open(self.path, "r", "shift_jisx0213") as f:
            for index, line in enumerate(f):
                string = line.strip()
                # get masslist
                if string.startswith('"測定質量数 '):
                    masslist = string.split('"')[2].split(",")
                    mlist = []
                    for m in masslist:
                        if m != "" and m != "--":
                            mlist.append(int(m))
                if string.startswith('"測定スピード'):
                    channels.append(string)
                if string.startswith('"SEM 電圧'):
                    params["sem"] = string.split(",")[1]

                if string.startswith('"選択 FIL'):
                    params["filament"] = string.split(",")[1][1:-1].strip()
                if string.startswith('"選択 SEM / FC'):
                    params["semfil"] = string.split(",")[1][1:-1].strip()
                if string.startswith('"測定開始日時 '):
                    params["start"] = string.split(",")[1].strip()
                    self.start = datetime.datetime.strptime(params["start"], "%Y/%m/%d %H:%M:%S")
                if string.startswith('"測定終了日時 '):
                    params["end"] = string.split(",")[1].strip()
                    self.end = datetime.datetime.strptime(params["end"], "%Y/%m/%d %H:%M:%S")
                if string.startswith('"レシピ名称  '):
                    try:
                        params["recipe"] = str(string.split(",")[1][1:-1]).strip()
                    except NameError:
                        params["recipe"] = str(string.split(",")[1][1:-1]).strip()
                if string.startswith('"イオン化電圧 '):
                    params["ionization"] = string.split(",")[1].strip()
                if string.startswith('"測定スピード   '):
                    params["mass_sampling"] = string.split(",")[1].strip()

                if string.startswith("1"):
                    break
            chName = ["No", "Time", "Trigger", "analog2", "qmsTP"]
            for m in mlist:
                chName.append("m%d" % m)

            self.colnames = chName
            self.skiprows = index
            self.stats = params
            self.masslist = [int(i[1:]) for i in self.colnames if i.startswith("m")]

    def load_data(self):
        """
        Generates DataFrame from qms data with proper datetime column for time
        """
        import pandas as pd
        from pandas import read_csv

        qmsdata = read_csv(
            self.path,
            skiprows=self.skiprows,
            delimiter=",",
            names=self.colnames,
            usecols=self.colnames,
            na_values=["-------", "-"],
            encoding="shift_jisx0213",
        )

        qmsdata.insert(0, "tsec", t2sa(qmsdata["Time"].values))
        timesec = pd.to_timedelta(qmsdata["tsec"], unit="s") + self.start
        qmsdata.insert(0, "date", timesec)

        self.data = qmsdata

    def slice(self, delta):
        """
        Slice DataFrame by datetime interval

        Parameters
        ----------
        delta: list
            list of datetime.dateme objects for the start and the end of an interval

        Returns
        -------
        data: pandas.DataFrame
            sliced qms dataframe
        """
        a = delta[0].strftime("%Y%m%d%H%M%S")
        b = delta[1].strftime("%Y%m%d%H%M%S")
        return self.data.query(f"{a} < date < {b}")

    def plot(self, **kws):
        """
        Plot time traces
        
        Parameters
        ----------
        masslist: list
            Specify list of masses to plot. Plots all by default.
        delta: list
            delta = [self.start, self.end] by default, datetime.datetime "window"
        ylim: list or tuple 
            axis ylims
        gridalpha: float
             transparancy of the grid lines
        figsize: tuple
            figure size, (8,6) by default
        rasterized: bool
            rasterized option for matplotlib
        colors: list
            list of colors for color cycle
        bbox_to_anchor: list or tuple
            bbox_to_anchor argument for matplotlib legend
        """
        import matplotlib.pyplot as plt
        from matplotlib.ticker import AutoMinorLocator

        fro, tto = kws.get("delta", [self.start, self.end])

        a = fro.strftime("%Y%m%d%H%M%S")
        b = tto.strftime("%Y%m%d%H%M%S")
        df = self.data.query(f"{a} < date < {b}")

        figsize = kws.get("figsize", (8, 6))

        fig = plt.figure(figsize=figsize, facecolor="w")
        ax = plt.gca()

        masslist = kws.get("masslist", self.masslist)
        rasterized = kws.get("rasterized", False)
        clrs = kws.get("colors", self.clr)

        [plt.plot(df["date"], df[f"m{i}"], label=f"m{i}", rasterized=rasterized, c=clrs[i]) for i in masslist]

        ax.set_xlabel("time")
        ax.set_ylabel("QMS Current, A")
        plt.xticks(rotation=25, ha="right")
        ylims = kws.get("ylim", False)
        if ylims:
            ax.set_ylim(ylims)

        txt = (
            f"{self.stats['start'].split()[0]} {self.stats['filament']} {self.stats['semfil']} "
            + f"{self.stats['sem']} {self.stats['recipe']} {self.stats['mass_sampling']} s/a.m.e"
        )
        ax.text(-0.15, 1.05, txt, transform=ax.transAxes)

        gridalpha = kws.get("gridalpha", [0.1, 0.3])
        qmsplotgrid(ax, gridalpha=gridalpha)
        qmsplotticks(ax)
        ax.set_yscale("log")

        axt = ax.twinx()
        trigger = self.data["Trigger"].values
        axt.plot(df["date"], df["Trigger"] / df["Trigger"].max(), "r")
        axt.set_ylim(0, 20)
        axt.axes.yaxis.set_ticks([])

        bbox_to_anchor = kws.get("bbox_to_anchor", [1, 1])
        ax.legend(loc=1, bbox_to_anchor=bbox_to_anchor)


def t2s(t):
    """
    Convert a time string of the Qulee format,
    '000:00:00.625' -> 'hhh:mm:ss.ms' to time in seconds.
    E.g '000:00:00.625' to 0.625 (s)
    
    Parameters
    ----------
    t: string
        Qulee time stamp string

    Returns
    -------
    t: datetime.timedelta
        datetime timedelta in seconds
    """
    import datetime, time

    ms = t.split(".")[1]
    hh = int(t.split(".")[0].split(":")[0])
    mm = t.split(".")[0].split(":")[1]
    ss = t.split(".")[0].split(":")[2]
    hoffset = 0
    if int(t.split(".")[0].split(":")[0]) > 23:
        hoffset = hh // 24
        tt = "0%d:%s:%s" % (hh - hoffset * 24, mm, ss)
    else:
        tt = "0%d:%s:%s" % (hh, mm, ss)
    x = time.strptime(tt, "0%H:%M:%S")
    return (
        datetime.timedelta(hours=hoffset * 24 + x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
        + float(ms) * 1e-3
    )


def t2sa(ta):
    """
    Convert an array of Qulee time stamp strings to array of datetime.timedelta in seconds.
    Just calls `t2s` in a loop.

    Parameters
    ----------
    ta: array-like
        array of time-strings from Qulee QMS
    
    Returns
    -------
    timearray: numpy.array
        numpy array with datetime.timedelta in seconds
    """
    import numpy as np

    return np.array([t2s(tt) for tt in ta])


def qmsplotgrid(ax, **kws):
    """
    QMS plot grid
    """
    gridalpha = kws.get("gridalpha", [0.1, 0.3])
    ax.grid(which="minor", linestyle="-", alpha=gridalpha[0])
    ax.grid(which="major", linestyle="-", alpha=gridalpha[1])


def qmsplotticks(ax):
    """
    QMS plot ticks
    """
    from matplotlib.ticker import LogLocator, AutoMinorLocator

    # Setup ticks
    xys = [ax.xaxis, ax.yaxis]
    [a.set_minor_locator(AutoMinorLocator()) for a in xys]
    ls = [7, 4]
    ws = [1, 0.8]
    [
        [a.set_tick_params(width=j, length=i, which=k) for i, j, k in zip(ls, ws, ["major", "minor"])]
        for a in xys
    ]


def tocsv(filename, **kws):
    """
    Convert `*.qst` binary into a `*.csv`. Works only with Quelee QMS software installed.

    Parameters
    ----------
    filename: string
        path to `*.qst` file.
    """
    import platform, sys, subprocess, os, time

    if not platform.system() == "Darwin":
        import win32api, win32con, win32com.client  # mouse control

        shell = win32com.client.Dispatch("WScript.Shell")  # this is to make a kay press

    try:
        retcode = subprocess.call("start " + filename, shell=True)
        if retcode < 0:
            print("Child was terminated by signal", retcode, file=sys.stderr)
        else:
            print("Child returned", file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)

    """Convert data to *.csv using this macro"""
    size = os.stat(os.path.join(filename)).st_size
    if size / 1.8e6 < 1:
        tsave = 1
    else:
        tsave = int(size / 2e6) + 1
    """ windows script to convert *.qst to *.csv"""
    tt = 0.2
    time.sleep(tt)
    shell.SendKeys("{ESC}")
    time.sleep(tt)
    shell.SendKeys("{ENTER}")
    time.sleep(tt + 1)
    shell.SendKeys("%ft")
    time.sleep(tt)
    shell.SendKeys("{ENTER}")
    time.sleep(tt)
    shell.SendKeys("y")
    time.sleep(tt)
    shell.SendKeys("{ESC}")
    time.sleep(tt + tsave)
    shell.SendKeys("%fc")
    time.sleep(tt)
    shell.SendKeys("{ESC}")
    """ close Qulee"""
    shell.SendKeys("%{F4}")


def generate_colors(masslist, **kws):
    """
    Generate colors based on masslist
    
    Parameters
    ----------
    masslist: list
            list of masses to be plotted
    cmap: matplotlib colormap for color cycle
    
    Returns
    -------
    clr: list
        list of colors
    """
    import matplotlib.pyplot as plt, numpy as np

    cmap = kws.get("cmap", plt.cm.twilight)

    color = cmap(np.linspace(0.1, 0.9, len(masslist)))
    clr = {i: j for i, j in zip(masslist, color)}
    clr[2] = "#ff421c"
    clr[3] = "#ffa305"
    clr[4] = "#6fff1c"
    clr[18] = "#05ffde"
    clr[28] = "#5983ff"
    clr[40] = "#ff4596"
    clr[32] = "#86ebc1"
    return clr


def plot_qms_dir(dir="", ls=[], out="batch_qms_plot.pdf", **kws):
    """
    Plot QMS files in a directory or from a list.

    Parameters
    ----------
    ls: list 
        list of absolute paths to files to plot
    dir: string
        directory to scan and plot
    out: string 
        output pdf file name or absolute path
    ext: string
        files extention, CSV by default
    figsize: float
        figure width, 500 by default
    anchor: list
        Matplotlib bbox_to_inches [1,1]
    rasterized: bool
        Matplotlib s rasterized option, when there are too many lines for a PDF
    ylim: list or tuple
           by default [1e-14,1e-5] 
    """
    import os, matplotlib.pyplot as plt, numpy as np
    from matplotlib.backends.backend_pdf import PdfPages
    import aklab.mpls as akmpl

    ext = kws.get("ext", "CSV")
    if not len(ls):
        if not len(dir):
            raise ValueError("either dir or ls must be provided, now both are empty")
        ls = os.listdir(dir)
        ls = [i for i in ls if i.endswith(ext)]
        ls = sorted(ls)[::-1]

    figsize = kws.get("figsize", 500)
    anchor = kws.get("anhcor", [1, 1])
    rasterized = kws.get("rasterized", True)
    ylim = kws.get("ylim", [1e-14, 1e-5])
    with PdfPages(out) as pdf:
        for i in ls:
            plt.style.use(os.path.join(package_directory, "notex.mplstyle"))
            qms = QMS(i)
            qms.plot(
                rasterized=rasterized, ylim=ylim, colors=generate_colors(qms.masslist, cmap=plt.cm.twilight)
            )
            fig = plt.gcf()
            fig.set_size_inches(akmpl.set_size(figsize))
            axs = fig.get_axes()
            axs[0].legend(bbox_to_anchor=anchor)
            # TODO: derive ticks from ylim
            axs[0].set_yticks(np.logspace(-14, -5, 14 - 5 + 1))
            akmpl.set_tick_size(plt.gca(), *(1, 4, 0.5, 2))
            pdf.savefig(dpi=300)
            plt.close()
