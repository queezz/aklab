import numpy as np
import matplotlib.pyplot as plt

class Qms:
    def __init__(self, datapath):
        self.data = None
        self.path = datapath
        # from os.path import join, exists, expanduser
        from os import makedirs
        from datetime import date
        self.date = date.today()
        # self.ppath = join(expanduser('~'), 'Dropbox','lab','programs','OxygenExperiments','out','qms',str(self.date))
        # if not exists(self.ppath):
        #     makedirs(f'../../out/qms/{self.date}')
        
        self.qms_file_parser()
        self.load_data()

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

        qms = read_csv(
            self.path,
            skiprows=self.skiprows,
            delimiter=",",
            names=self.colnames,
            usecols=self.colnames,
            na_values=["-------", "-"],
            encoding="shift_jisx0213",
        )

        qms.insert(0, "tsec", t2sa(qms["Time"].values))
        timesec = pd.to_timedelta(qms["tsec"], unit="s") + self.start
        qms.insert(0, "date", timesec)

        self.data = qms

    def plot(self, **kws):
        """plot time traces
        kws:
        masslist: specify list of masses to plot. Plots all by default.
        fro: starting time, self.start by default.
        to: ending time, self.end by default
        ylim: axis ylims
        gridalpha: transparancy of the grid lines
        """
        import matplotlib.pylab as plt
        from matplotlib.ticker import AutoMinorLocator

        fro = kws.get("fro", self.start)
        tto = kws.get("tto", self.end)

        log = kws.get("log",True)

        a = fro.strftime("%Y%m%d%H%M%S")
        b = tto.strftime("%Y%m%d%H%M%S")
        df = self.data.query(f"{a} < date < {b}")

        fig = plt.figure(figsize=(8, 6), facecolor="w")
        ax = plt.gca()

        masslist = kws.get("masslist", self.masslist)

        [plt.plot(df["date"], df[f"m{i}"], label=f"m{i}") for i in masslist]

        plt.legend(loc=1, bbox_to_anchor=[1.23, 1.1])
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
        if log:
            ax.set_yscale("log")

        axt = ax.twinx()
        trigger = self.data["Trigger"].values
        axt.plot(df["date"], df["Trigger"] / df["Trigger"].max(), "k")
        axt.set_ylim(0, 20)
        axt.axes.yaxis.set_ticks([])

        self.df = df

def qms_ig_calibration(raspi, qms, rangeis,gain = 1, show_summary = False, mass_select='2',style=False,xoffset=None,yoffset=None):
    mass = 'm' + mass_select
    # raspi_calib = raspi.drop(list(range(rangeis[0]))).drop(list(range(rangeis[1],len(raspi)))).reset_index(drop=True)[['date','time','pd']]

    a = rangeis[0].strftime("%Y%m%d%H%M%S")
    b = rangeis[1].strftime("%Y%m%d%H%M%S")
    raspi_calib = raspi.adc.query(f"{a} < date < {b}").reset_index(drop=True)[['date','time','pd']]
    qms_calib = qms.data.query(f"{a} < date < {b}").reset_index(drop=True)[[mass,'tsec']]

    # add_strdatetime(raspi_calib)
    # add_strdatetime(qms)

    # st = raspi_calib['date_str'][0]
    # et = raspi_calib['date_str'][len(raspi_calib)-1]
    # si_qms = qms[qms['date_str'].str.startswith(st)].index[0]
    # ei_qms = qms[qms['date_str'].str.startswith(et)].index[0] + 1

    fitting_time = raspi_calib['date'][len(raspi_calib)-1] - raspi_calib['date'][0]

    # rangeis = [si_qms,ei_qms]
    # qms_calib = qms.drop(list(range(rangeis[0]))).drop(list(range(rangeis[1],len(qms)))).reset_index(drop=True)[[mass,'tsec']]

    num_raspi = len(raspi_calib)
    num_qms = len(qms_calib)
    num_interpolation = num_raspi - num_qms
    dense = num_interpolation / (num_qms-1)

    """m2のデータを線形補完"""
    a = [] #補完の区切りを作成
    j = 1
    for i in range(num_interpolation):
        if i > j*dense:
            a += [i-1]
            j += 1

    a += [num_interpolation]

    j = 0 #各区間に何個の補完を行うか
    b = []
    for i in a:
        b += [i-j]
        j = i


    c = [] #線形補完
    for i in range(len(b)):
        c += [qms_calib[mass][i]]
        d = (qms_calib[mass][i+1] - qms_calib[mass][i])/(b[i]+1)
        for j in range(b[i]):
            c += [qms_calib[mass][i] + d*(j+1)]

    c += [qms_calib[mass][len(qms_calib)-1]]


    import statsmodels.api as sm
    x = c
    y = np.array(raspi_calib['pd'])*gain
    mod = sm.OLS(y, sm.add_constant(x))
    res = mod.fit()
    c1 = res.params[0]
    k1 = res.params[1]
    h = []
    for i in range(len(x)):
        h += [x[i] * k1]

    if show_summary:
        print(res.summary())

    print(f'{fitting_time}秒間のデータを利用')

    print(f'Proportional constant P/current is {k1}')



    font_setup(size=28)

    if style:
        if xoffset and yoffset:
            fig = plt.figure(figsize=(16, 9), dpi=50)
            a = r"$p_{\rm ig}$ $({\rm {\times}10^{";b = f"{yoffset}";c = r"}{\ }Torr})$"
            d = r"$I{\ }({\rm {\times}10^{";e = f"{xoffset}";f = r"}{\ }A})$"
            ax = fig.add_subplot(1,1,1, xlabel=(d+e+f), ylabel=(a+b+c))
            ax.xaxis.offsetText.set_fontsize(0)
            ax.yaxis.offsetText.set_fontsize(0)
            l1 = [ax.scatter(x,y, label='QMSsignal-IG',c='k')]
            l2 = ax.plot(x, c1+h, label='Fitting',c='r')
            ax.legend(handles=l1+l2, labels=['Data','Fitting'])
            ticks_visual(ax)
            grid_visual(ax)
            ax.set_ylim(0,max(y)*1.1)
            ax.set_xlim(right=2.25e-7)
            ax.set_xticks([i for i in np.linspace(0,2.25e-7,10)])
            return k1, c1

        else:
            print('input offset!')
            return False, False
    else:
        fig = plt.figure(figsize=(16, 9), dpi=50)
        ax = fig.add_subplot(1,1,1, xlabel="QMS Current [A]", ylabel=r"$P_{\rm per}$ [Torr]")
        ax.scatter(x,y, label='QMSsignal-IG')
        ax.plot(x, c1+h, label='Fitting')
        ax.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=0, fontsize=28)
        ticks_visual(ax)
        grid_visual(ax) 
        return k1, c1



def fft_filtering(sample, dt,fc):
    # ローパスフィルタ
    N = len(sample)           # サンプル数
    # dt is サンプリング間隔   
    t = np.arange(0, N*dt, dt) # 時間軸
    freq = np.linspace(0, 1.0/dt, N) # 周波数軸

    # fc = 0.1        # カットオフ周波数
    fs = 1 / dt     # サンプリング周波数
    # fm = (1/2) * fs # アンチエリアジング周波数
    fc_upper = fs - fc # 上側のカットオフ　fc～fc_upperの部分をカット

    # 元波形をfft
    F = np.fft.fft(sample)

    # 元波形をコピーする
    G = F.copy()

    # ローパス
    G[((freq > fc)&(freq< fc_upper))] = 0 + 0j

    # 高速逆フーリエ変換
    g = np.fft.ifft(G)

    # 実部の値のみ取り出し
    return np.array(g.real)



def add_strdatetime(df):
    date_str = []
    for i in range(len(df)):
        date_str.append(df['date'][i].strftime("%Y/%m/%d %H:%M:%S"))

    df['date_str'] = date_str   





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



# Matploblib adjustments
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
    import matplotlib.pyplot as plt

    ticks_visual(plt.gca())
    grid_visual(plt.gca())
    return


def font_setup(size=28, weight="normal", family="serif"):
    import matplotlib.pyplot as plt
    from matplotlib import rc

    plt.rcParams["font.family"] = family
    plt.rcParams["font.size"]   = size
    plt.rcParams["font.weight"] = weight
    rc('mathtext', **{'rm': 'serif',
                      'it': 'serif:itelic',
                      'bf': 'serif:bold',
                      'fontset': 'cm'})