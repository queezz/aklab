"""
"Qulee" (pronounced as "KLEE"), is ULVAC's latest model for residual gas analysis. 

Tools to work with Qulee mass spectrometer outputs (CSV) and maybe later with Qulee software?
Created 2021/06/11 by queezz
"""
from aklab.constants import *


class QMS:
    """Class for reading, processing, and storing Qulee QMS data"""

    def __init__(self, datapath):
        """ """
        self.data = None
        self.path = datapath
        self.qms_file_parser()
        self.load_data()
        self.generate_colors()

    def qms_file_parser(self):
        """ " Given filepath to ULVAC's Qulee BGM QMS file, converted to *.csv,
        Parses the header, extracts column names, QMS settings, and line number where data starts
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
        """Return qms data with proper datetime column for time
        1. parse header using qms_file_parser
        2. read csv file
        Convert time
        3. convert qms time format from '000:00:00.00' to
        a) seconds and append to dataframe, and
        b) proper datetime object with correct time and date
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

    def generate_colors(self):
        """ Generate colors based on masslist"""
        import matplotlib.pylab as plt
        import numpy as np

        color = plt.cm.hsv(np.linspace(0.1, 0.9, len(self.masslist)))
        clr = {i: j for i, j in zip(self.masslist, color)}
        clr[2] = "#ff421c"
        clr[3] = "#ffa305"
        clr[4] = "#6fff1c"
        self.clr = clr

    def plot(self, **kws):
        """plot time traces
        kws:
        masslist: specify list of masses to plot. Plots all by default.
        from: starting time, self.start by default.
        to: ending time, self.end by default
        ylim: axis ylims
        gridalpha: transparancy of the grid lines
        """
        import matplotlib.pylab as plt
        from matplotlib.ticker import AutoMinorLocator

        fro = kws.get("fro", self.start)
        tto = kws.get("tto", self.end)

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
        customgrid(ax, gridalpha=gridalpha)
        customticks(ax)
        ax.set_yscale("log")

        axt = ax.twinx()
        trigger = self.data["Trigger"].values
        axt.plot(df["date"], df["Trigger"] / df["Trigger"].max(), "r")
        axt.set_ylim(0, 20)
        axt.axes.yaxis.set_ticks([])

        ax.legend(loc=1, bbox_to_anchor=[1, 1])


def t2s(t):
    """
    Converts QMS timing into seconds.
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
    convert an array of strings of the Qulee format: '000:00:00.625' to time in seconds.
    '000:00:00.625' -> 'hhh:mm:ss.ms'
    """
    import numpy as np

    return np.array([t2s(tt) for tt in ta])


def customgrid(ax, **kws):
    # Setup grid
    gridalpha = kws.get("gridalpha", [0.1, 0.3])
    ax.grid(which="minor", linestyle="-", alpha=gridalpha[0])
    ax.grid(which="major", linestyle="-", alpha=gridalpha[1])


def customticks(ax):
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
    """ Convert native binary into csv with Quelee software installed."""
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
    """ Generate colors based on masslist"""
    import matplotlib.pylab as plt, numpy as np

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
    """ Provided dir, reads all converted Quelee *.csv's and plots into a PDF
    ls: list of absolute paths to files to plot
        OR
    dir: directory to scan and plot
    out: output pdf file name or absolute path
    ext = kws.get('ext','CSV')
    figsize = kws.get('figsize',500)
    anchor= kws.get('anhcor',[1,1])
    rasterized = kws.get('rasterized',True)
    ylim = kws.get('ylim',[1e-14,1e-5])
    """
    import os, matplotlib.pylab as plt, numpy as np
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
