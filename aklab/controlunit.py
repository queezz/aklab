"""
Tools to read logger data from plasma control unit https://github.com/queezz/ControlUnit
"""

from re import S
import pandas as pd
from aklab import mpls as akmp
from aklab import convert


class Raspi:
    def __init__(self, bpath="", timestamp=""):
        """
        Read two files from basepath `bpath` with same `timestamp`, 
        one with ADC signals, another with Thermocouple signal.

        Parameters
        ----------
        bpath: string
            path to datafolder
        timestamp: string
            timestamp for both files
        """
        from datetime import date

        self.bpath = bpath
        self.stamp = timestamp
        self.date = date.today()

        self.skip = 0
        self.load_data()
        # return if no adc data found
        if self.skip == 2:
            return

        self.convert_signals()
        self.update_dataframes()

    def load_data(self) -> int:
        """load data"""
        from datetime import datetime
        from os.path import join
        import warnings

        start = datetime.strptime(self.stamp, "%Y%m%d_%H%M%S")
        self.start = start

        try:
            fpth = f"out_{self.stamp}_temp.csv"
            self.tc = pd.read_csv(join(self.bpath, fpth))
            self.tc.insert(
                0, "date", start + pd.to_timedelta(self.tc["time"], unit="s")
            )
            self.end = self.tc["date"].iloc[-2].to_pydatetime()
            # just for convenience, df - dataframe.
            self.df_tc = self.tc
        except FileNotFoundError:
            warnings.warn(f"Temperature file not found: {fpth}")
            self.skip = 1
        try:
            fpth = f"out_{self.stamp}.csv"
            self.adc = pd.read_csv(join(self.bpath, fpth))
            self.adc.insert(
                0, "date", start + pd.to_timedelta(self.adc["time"], unit="s")
            )
            self.end = self.adc["date"].iloc[-2].to_pydatetime()
            # just for convenience, df - dataframe.
            self.df_adc = self.adc
        except FileNotFoundError:
            warnings.warn(f"ADC file not found, conversion skipped: {fpth}")
            if self.skip == 1:
                raise FileNotFoundError(f"No data found in\n{self.bpath}")
            self.skip = 2

    def convert_signals(self):
        """
        Convert analogue signals.
        """
        self.pu = convert.pfeiffer_sg(self.adc["P2"])
        self.pd = convert.ionization_gauge(self.adc["P1"], self.adc["IGscale"])
        self.ip = convert.hall_sensor(self.adc["Ip"])
        self.t = self.adc["date"]

    def update_dataframes(self):
        """
        Insert columns with converted signals into self.adc
        """
        self.adc.insert(1, "pu", self.pu)
        self.adc.insert(1, "pd", self.pd)
        self.adc.insert(1, "ip", self.ip)

    def plot(self, **kws):
        """
        Plot time traces for all signals.

        Keyword Arguments
        -----------------
        lims: list
            default lims = [[5e-8, 2e-6], [-0.2, 2.5], [0, 350]]

        """
        import matplotlib.dates as mdates
        import matplotlib.pylab as plt
        from matplotlib.ticker import LogLocator, AutoMinorLocator

        fro = kws.get("fro", self.start)
        tto = kws.get("tto", self.end)
        rasterized = kws.get("rasterized", True)

        a = fro.strftime("%Y%m%d%H%M%S")
        b = tto.strftime("%Y%m%d%H%M%S")
        if not self.skip == 2:
            df_adc = self.adc.query(f"{a} < date < {b}")
        if not self.skip == 1:
            df_tc = self.tc.query(f"{a} < date < {b}")

        fig = plt.figure(figsize=(12, 8), facecolor="w")
        gs = plt.GridSpec(4, 1)
        gs.update(left=0.1, right=0.95, wspace=0.2, hspace=0.14)
        ax0 = plt.subplot(gs[:2, 0])  # sharex=ax0
        axs = [ax0] + [plt.subplot(gs[i, 0], sharex=ax0) for i in range(2, 4)]

        plottrig = 0

        def plot_trig(axt):
            axt.plot(
                df_adc["datetime"],
                df_adc["QMS_signal"],
                "C2",
                label="trig",
                rasterized=rasterized,
            )
            axt.set_yticks([])

        if plottrig:
            twins = [ax.twinx() for ax in [axs[0], axs[1], axs[2]]]
            [plot_trig(ax) for ax in twins]
            twins[0].legend(loc=1, bbox_to_anchor=[0.2, 1.2])

        if not self.skip == 2:
            ax = axs[0]
            ax.plot(
                df_adc["date"],
                df_adc["pd"],
                "-",
                c="k",
                label="Permeation Chamber",
                rasterized=rasterized,
            )
            ax.plot(
                df_adc["date"],
                df_adc["pu"],
                "-",
                c="C3",
                label="Plasma Chamber",
                rasterized=rasterized,
            )
            ax.locator_params(axis="y", nbins=6)

            ax.legend(loc=1, ncol=2, bbox_to_anchor=[1.0, 1.2])

            ax = axs[1]

            ax.plot(
                df_adc["date"],
                df_adc["ip"] - df_adc["ip"][:100].mean(),
                "k",
                rasterized=rasterized,
            )

        if not self.skip == 1:
            ax = axs[2]
            ax.plot(df_tc["date"], df_tc["T"], c="k", rasterized=rasterized)
            ax.plot(df_tc["date"], df_tc["PresetT"], "C2--", rasterized=rasterized)
            plt.xticks(rotation=25, ha="right")

        gridalpha = kws.get("gridalpha", [0.1, 0.3])
        [akmp.grid_visual(ax, alpha=gridalpha) for ax in axs]
        [akmp.ticks_visual(ax) for ax in axs]
        axs[0].set_yscale("log")

        lbls = ["P [Torr]", "$I_p$ [A]", "T [$^{\\circ }$C]"]
        [ax.set_ylabel(l) for l, ax in zip(lbls, axs)]
        axs[-1].set_xlabel(f"time")

        lims = kws.get("lims", [[5e-8, 2e-6], [-0.2, 2.5], [0, 350]])
        [ax.set_ylim(l) for ax, l in zip(axs, lims)]
        axs[-1].locator_params(
            axis="y", nbins=5
        )  # increas number of major ticks for T plot
        locmax = LogLocator(base=10, subs=(1.0,), numticks=100)
        axs[0].yaxis.set_major_locator(locmax)

        [ax.xaxis.set_minor_locator(AutoMinorLocator(2)) for ax in axs]
        [ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %H:%M")) for ax in axs]

        # [ax.axes.xaxis.set_ticklabels([]) for ax in axs[:-1]]
        [plt.setp(ax.get_xticklabels(), visible=False) for ax in axs[:-1]]

        ax = axs[-1]
        plt.sca(ax)  # set current axis
        plt.xticks(rotation=25, ha="right")
        ax = axs[0]
        ax.text(
            -0.05,
            1.07,
            self.start.strftime("%Y, %d %b, %a, %H:%M"),
            transform=ax.transAxes,
        )
        ax = axs[2]
        ax.text(
            -0.05,
            -0.8,
            timedelta_to_str(self.end - self.start),
            transform=ax.transAxes,
        )


def plot_raspi_batch(ts=[], bpth=".", out="batch_raspi_plot.pdf", **kws):
    """
    Plot Control Unit data for a list of files or a dir.
    
    Parameters
    ----------
    ts: list
        list of timestamps to plot
    bpth: string
        path to data folder
    out: string
        ouptupt file name or path
    """
    import os, matplotlib.pyplot as plt, numpy as np
    from matplotlib.backends.backend_pdf import PdfPages
    import aklab.mpls as akmpl
    from aklab import constants
    from tqdm import tqdm_notebook
    import gc

    figsize = kws.get("figsize", 500)
    rasterized = kws.get("rasterized", True)
    lims = kws.get("lims", [[5e-8, 2e-6], [-0.2, 2.5], [0, 350]])
    with PdfPages(out) as pdf:
        for i in tqdm_notebook(ts):
            try:
                plt.style.use(
                    os.path.join(constants.package_directory, "notex.mplstyle")
                )
                raspi = Raspi(bpth, i)
                raspi.plot(rasterized=rasterized, lims=lims)
                fig = plt.gcf()
                fig.set_size_inches(akmpl.set_size(figsize))
                akmpl.set_tick_size(plt.gca(), [1, 4, 0.5, 2])
                pdf.savefig(dpi=300, bbox_inches="tight")
                fig.clf()
                plt.close()
                del raspi
                raspi = "string"
                gc.collect
            except Exception as e:
                print(f"Skipping {i}\n{e}")


def extract_timestamp(filename):
    """
    Extract time stamp from adc or tc csv file name

    Parameters
    ----------
    filename: string
        basename of a Raspi logger file, ADC or TC
    """
    return "_".join(filename.split("_")[1:3]).split(".")[0]


def timedelta_to_str(td):
    """
    from datetime.timedelta calculate
    days, hours ans minuts, return formatted string
    """
    return f"{td.days} days, {td.seconds//3600} hours, {(td.seconds//60)%60} minutes"
