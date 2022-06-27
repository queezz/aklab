from os.path import join
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

class Langmuirprobe(object):
    def __init__(self,date,species):
        import os
        self.bp = join('../../data/langmuirprobe',date)
        self.species = species
        self.df = []
        for i in os.listdir(self.bp):
            self.df.append(pd.read_csv(join(self.bp, i), skiprows=9, usecols=[0,1,2], names=('Time', 'Signal1', 'Signal2')))
        self.df = self.plot_row_image()
        self.plot_vp_ip()
        self.df_c = self.fitting_and_dividing()
        



    def plot_row_image(self,disp=False):
        r1 = 100
        r2 = 1e3
        r3 = 1e6

        for i in range(len(self.df)):
            self.df[i]["vp"] = -self.df[i]["Signal2"] * (r2 + r3) / r2
            self.df[i]["ip"] = self.df[i]["Signal1"] / r1 * 1000 - self.df[i]["Signal2"] / r2 * 1000

        if disp:
            plt.plot(self.df[0]["Time"], self.df[0]["vp"])
            plt.plot(self.df[0]["Time"], self.df[0]["ip"])

        return self.df

    def plot_vp_ip(self):
        fig = plt.figure(figsize=(12, 6), dpi=50)
        xdivision = 1
        font_setup(size="28")

        ax = fig.add_subplot(1,2,1)
        ax.set_xlabel(r"$T$${\ }$$({\rm s})$")
        ax.set_ylabel(r"$V_{\rm p}$${\ }$$({\rm V})$")
        ax.plot(self.df[0]["Time"], self.df[0]["vp"],c="black")
        ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(xdivision))
        ticks_visual(ax)
        grid_visual(ax)

        ax = fig.add_subplot(1,2,2)
        ax.set_xlabel(r"$T$${\ }$$({\rm s})$")
        ax.set_ylabel(r"$I_{\rm p}$${\ }$$({\rm mA})$")
        ax.plot(self.df[0]["Time"], self.df[0]["ip"],c="black")
        ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(xdivision))
        ticks_visual(ax)
        grid_visual(ax)

        plt.tight_layout()

    def fitting_and_dividing(self,dt=1e-5,fc=100):
        df_c = []
        for i in range(len(self.df)):
            vp = 0
            ip = 0
            for j in range(5):
                vp += self.df[i]["vp"][100000*j:100000*(j+1)+1].reset_index(drop=True)
                ip += self.df[i]["ip"][100000*j:100000*(j+1)+1].reset_index(drop=True)

            df_c_temp = pd.DataFrame(index=[], columns=['Time', 'vp', 'ip'])
            df_c_temp["vp"] = vp / 5
            df_c_temp["ip"] = ip / 5
            df_c_temp["Time"] = self.df[i]["Time"][0:100001]
            df_c.append(df_c_temp)

        for i in range(len(df_c)):
            df_c[i]["vp_f"] = fft_filtering(df_c[i]["vp"],dt,fc)
            df_c[i]["ip_f"] = fft_filtering(df_c[i]["ip"],dt,fc)
        fig = plt.figure(figsize=(12,6),dpi=50)
        ax = fig.add_subplot(111)
        ax.plot(df_c[0]["Time"], df_c[0]["ip"])
        ax.plot(df_c[0]["Time"], df_c[0]["vp"])
        ax.plot(df_c[0]["Time"], df_c[0]["ip_f"])
        ax.plot(df_c[0]["Time"], df_c[0]["vp_f"])
        ticks_visual(ax)
        grid_visual(ax)


        return df_c

    def line_cross_point(self, borders):
        x0, y0 = borders[0]
        x1, y1 = borders[1]
        x2, y2 = borders[2]
        x3, y3 = borders[3]
        a0 = x1 - x0
        b0 = y1 - y0
        a2 = x3 - x2
        b2 = y3 - y2

        d = a0*b2 - a2*b0
        if d == 0:
            return False
        else:
            sn = b2 * (x2-x0) - a2 * (y2-y0)
            return x0 + a0*sn/d, y0 + b0*sn/d

    def set_point(self,point=[[50000,50200,51000,52000]]):
        import matplotlib as mpl
        import math
        bd_range = [40000,60000]
        if len(point) == 1:
            self.bd = [point[0]]*len(self.df_c)
        elif len(point) == len(self.df_c):
            self.bd = point
        self.cross_point_vp = [0] * len(self.df_c)
        self.cross_point_index = [0] * len(self.df_c)
        for i in range(len(self.df_c)):
            borders = [(self.df_c[i]["vp_f"][self.bd[i][j]],math.log10(self.df_c[i]["ip_f"][self.bd[i][j]])) for j in range(4)]
            if self.line_cross_point(borders):
                self.cross_point_vp[i] = self.line_cross_point(borders)[0]
                self.cross_point_index[i] = np.argmin(np.abs([self.df_c[i]["vp_f"][j] for j in range(bd_range[0], bd_range[1])] - self.cross_point_vp[i]))+bd_range[0]
            else:
                self.cross_point_vp[i] = None
                self.cross_point_index[i] = None
        
        fig = plt.figure(figsize=(24, 16), dpi=50)

        for i in range(len(self.df_c)):
            xdivision = 2.5
            ax = fig.add_subplot(2,3,i+1)
            ax.set_xlabel(r"$V_{\rm p}$${\ }$$({\rm V})$")
            ax.set_ylabel(r"$I_{\rm p}$${\ }$$({\rm mA})$")
            ax.plot(self.df_c[i]["vp_f"][bd_range[0]:bd_range[1]],self.df_c[i]["ip_f"][bd_range[0]:bd_range[1]],c="black",label=self.species[i])
            ax.legend(bbox_to_anchor=(0, 1), loc='upper left', borderaxespad=0, fontsize=28)
            ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(xdivision))
            ax.set_yscale('log')
            plt.xlim([-5,10])
            plt.ylim([2,50])
            font_setup(size="28")
            ticks_visual(ax)
            grid_visual(ax)

            for j in self.bd[i]:
                plt.scatter(self.df_c[i]["vp_f"][j],self.df_c[i]["ip_f"][j],marker='o',s=400,c="black")
            
            j = self.cross_point_index[i]
            plt.scatter(self.df_c[i]["vp_f"][j],self.df_c[i]["ip_f"][j],marker='s',s=400,c="black")
        
    def calc(self,plot=True,tlim=None,nlim=None,style=False,noffset=None):
        from scipy.constants import e,m_e,k
        import math
        r = 0.25e-3
        h = 3.5e-3
        a = np.pi*r**2 + 2*np.pi*r*h #Surface area
        self.ev = [0] * len(self.df_c) # Electron temperature [eV]
        self.ne = [0] * len(self.df_c) # Electron density [/m^3]
        for i in range(len(self.df_c)):
            self.ev[i] = (self.df_c[i]["vp_f"][self.bd[i][0]] - self.df_c[i]["vp_f"][self.bd[i][1]]) / (math.log(self.df_c[i]["ip_f"][self.bd[i][1]]) - math.log(self.df_c[i]["ip_f"][self.bd[i][0]])) * e / k / 11609 * -1
            self.ne[i] = self.df_c[i]["ip_f"][self.cross_point_index[i]] / 1000.0 / (e*(k*self.ev[i]*11609.0/2.0/np.pi/m_e)**0.5*a)

        if plot:
            self.plot_result(ylim1=nlim,ylim2=tlim,style=style,noffset=noffset)
        

    def plot_result(self,ylim1=[0,8e16],ylim2=[0,10],style=False,noffset=None):
        fig = plt.figure(figsize=(12, 8), dpi=40)
        ax2 = fig.add_subplot(1,1,1)

        ax2.scatter(self.species,self.ev,marker='o',s=400,c="black",label=r"${\rm measured}$${\ }$$T_{\rm e}$")
        ax2.set_ylim(ylim2)

        ax2.set_xlabel(r"$O_2$ concentration (%)")
        ax2.set_ylabel(r"$T_{\rm e}$${\ }$$({\rm eV})$")
        xdivision = 1
        ax2.xaxis.set_major_locator(mpl.ticker.MultipleLocator(xdivision))
        font_setup(size="28")
        ticks_visual(ax2)
        grid_visual(ax2)

        ax = ax2.twinx()
        ax.scatter(self.species,self.ne,marker='s',s=400,c="black",label=r"${\rm measured}$${\ }$$n_{\rm e}$")
        ax.set_ylim(ylim1)

        plt.xticks(self.species)
        if style:
            ax.yaxis.offsetText.set_fontsize(0)
            if noffset:
                a = r"$n_{\rm e}$${\ }$$({\rm {\times}10^{"
                b = str(noffset)
                c = r"}{\ }m^{-3}})$"
                ax.set_ylabel(a+b+c)
            elif not noffset:
                ax.set_ylabel(r"$n_{\rm e}$${\ }$$({\rm m^{-3}})$")
        else:
            ax.set_ylabel(r"$n_{\rm e}$${\ }$$({\rm m^{-3}})$")

        h1, l1 = ax2.get_legend_handles_labels()
        h2, l2 = ax.get_legend_handles_labels()
        ax2.legend(h1+h2, l1+l2, loc='upper left',bbox_to_anchor=(0, 1),borderaxespad=0)

        plt.tight_layout()

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