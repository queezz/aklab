"""
Horiba Jobin Yvon spectrometer, focal length="", with which_camera.
Script to read data?
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import xarray as xr
import pandas as pd
import numpy as np
from os.path import join, exists

import aklab.mpls as akmp


class Spectrometer:
    def __init__(self, bpath="", disp=True, old=None, subtract=False, bgpath=None):

        from os import listdir
        from datetime import date

        self.bpath = bpath
        self.date = date.today()
        self.wavelength = 0
        self.old = old
        self.balmers = np.array([656.279, 486.135, 434.047])  # Halph, Hbeta, Hgammma

        if self.old:  # for analysis befor 2021/11/21
            self.rs = np.array([22000, 60570, 70730])
        else:
            self.rs = np.array([84815, 123253, 133373])

        self.fun = np.poly1d(np.polyfit(self.rs, self.balmers, 2))
        # self.basefiles = listdir(bpath)

        self.fp_list = []
        for i in range(len(listdir(bpath))):
            rotation = int(listdir(bpath)[i].split("-")[1])
            self.fp_list.append([join(bpath, listdir(bpath)[i]), rotation])
        self.fp_df = pd.DataFrame(self.fp_list, columns=["filepath", "rotation"])

        self.data_list = []
        list_id = []

        for i in listdir(bpath):  # convert all nc files in basepath to np.ndarray
            self.data_list.append(self.convert_nc(i))
            list_id.append(i)

        print(pd.DataFrame(list_id, columns=["index of data_list"]))

        if disp:
            for i in self.fp_list:
                if subtract:
                    self.display_nc(self.sub_bg(i[0], bgpath))
                else:
                    self.display_nc(i[0])
                plt.title(f"{i[0]}")

    def rotationis(self, rotation):
        if self.old:
            if rotation == 400000:
                wavelength = self.balmers[0]
            elif rotation == 585000:
                wavelength = self.balmers[1]
            elif rotation == 635000:
                wavelength = self.balmers[2]
            else:
                wavelength = 0
        else:
            if rotation == 415000:
                wavelength = self.balmers[0]
            elif rotation == 600000:
                wavelength = self.balmers[1]
            elif rotation == 650000:
                wavelength = self.balmers[2]
            else:
                wavelength = 0

        return wavelength

    def get_rot(self, fp):
        if iscd(fp):
            return int(fp.split("-")[1])
        elif exists(fp):
            split = "\\"
            if len(fp.split(split)) == 1:
                split = "/"
            return int(fp.split(split)[-1].split("-")[1])
        else:
            print("File does not exist")
            return

    def convert_nc(self, fp):
        if iscd(fp):
            fp = join(self.bpath, fp)
            if not exists(fp):
                print("File does not exist")
                return
        rotation = self.get_rot(fp)
        data = np.array(xr.open_dataset(fp).to_array()[0].sum(axis=0)).astype(np.float64)
        if self.old:
            data = np.stack([data, self.fun(np.arange(2048) + (rotation - 300000) * 1044.5 / 5000)], 0)
        else:
            data = np.stack([data, self.fun(np.arange(2048) + (rotation - 10000) * 1039.67 / 5000)], 0)

        return data

    def display_nc(
        self,
        fp,
        xlim=None,
        ylim=None,
        disp=True,
        subplot=None,
        fig=None,
        style=False,
        yoffset=None,
        title=None,
        line=None,
    ):
        if type(fp) == str:  # when row nc data is selected
            data = self.convert_nc(fp)
        elif type(fp) != np.ndarray:
            return 'please insert fp="row nc data" or data="converted nc data"'
        else:
            data = fp
        akmp.font_setup(size=28)
        if disp:
            if subplot:
                ax = fig.add_subplot(
                    subplot[0], subplot[1], subplot[2], xlabel=r"${\rm Wavelength}{\ }{\rm (nm)}$"
                )
            else:
                fig = plt.figure(figsize=(16, 9), dpi=50)
                ax = fig.add_subplot(1, 1, 1, xlabel=r"${\rm Wavelength}{\ }{\rm (nm)}$")
            if line:
                ax.axvline(line, c="r")
            if style:
                a = r"${\rm Intensity}{\ }{\rm (\times 10^"
                b = f"{yoffset}"
                c = r"{\ }arb.unit)}$"
                ax.set_ylabel(a + b + c)
                ax.set_ylabel(r"${\rm Intensity}{\ }{\rm (arb.unit)}$")
                ax.yaxis.offsetText.set_fontsize(0)
                ax.plot(data[1], data[0] / max(data[0]), ".-", c="k")
            else:
                ax.set_ylabel(r"${\rm Intensity}{\ }{\rm (arb.unit)}$")
                ax.plot(data[1], data[0], ".-", c="k")
                ax.set_ylim(top=max(data[0]) * 1.2)

            ax.set_title(title)
            # ax.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=0, fontsize=16)
            akmp.ticks_visual(ax)
            akmp.grid_visual(ax)
            if xlim:
                ax.set_xlim(xlim)
            if ylim:
                ax.set_ylim(ylim)

    def subtract_background(self, fp, disp=True, bp=None):
        split = "\\"
        from os.path import join

        if not bp:
            bp = join("../../data/spectrometer/20211208", "background-420000-10000.0ms-.nc")
        image = self.convert_nc(fp)
        back = self.convert_nc(bp)
        sub = image
        for i in range(len(image[0])):
            sub[0][i] = image[0][i] - back[0][i]
        if disp:
            fig = plt.figure(figsize=(16, 9), dpi=50)
            ax = fig.add_subplot(
                1,
                1,
                1,
                xlabel=r"${\rm Wavelength}{\ }{\rm (nm)}$",
                ylabel=r"${\rm Intensity}{\ }{\rm (arb.unit)}$",
            )
            ax.plot(sub[1], sub[0], ".-")
            # ax.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=0, fontsize=16)
            akmp.ticks_visual(ax)
            akmp.grid_visual(ax)
        return sub

    def sub_bg(self, fp, bgpath):
        import os

        rot = fp.split("-")[1]
        op = fp.split("-")[4]
        ls = [i for i in os.listdir(bgpath) if rot in i]
        ls = [i for i in ls if "-" + op + "-" in i]
        if ls == []:
            ls = [os.listdir(bgpath)]
        return self.subtract_background(fp, disp=False, bp=os.path.join(bgpath, ls[0]))

        # def display_nc(self, name, xlimit=0, ylimit=0, disp=0, topng=False, topdf=False):
        import re
        from os.path import join

        numbers = re.findall(r"\d+", name)
        rotation_number = []
        for i in range(len(numbers)):
            if int(numbers[i]) // 5000 != 0:
                rotation_number.append(numbers[i])
        self.rotationis(rotation_number[0])

        fp = join(self.bpath, name)
        data = np.array(xr.open_dataset(fp).to_array()[0].sum(axis=0)).astype(np.float64)
        data = np.stack([data, self.fun(np.arange(2048) + (self.rotation - 300000) * 1044.5 / 5000)], 0)
        if xlimit == 0:
            x = data[1]
            y = data[0]
        else:
            n = self.idx_of_the_nearest(data[1], xlimit)
            x = data[1][n[1] : n[0]]
            y = data[0][n[1] : n[0]]

        if disp == 0:
            # xdivision = 200
            font_setup(size=28)
            fig = plt.figure(figsize=(16, 9), dpi=50)
            ax = fig.add_subplot(
                1,
                1,
                1,
                xlabel=r"${\rm Wavelength}{\ }{\rm (nm)}$",
                ylabel=r"${\rm Intensity}{\ }{\rm (arb.unit)}$",
            )
            ax.plot(data[1], data[0], ".-", label=name)
            ax.legend(bbox_to_anchor=(1, 1), loc="upper right", borderaxespad=0, fontsize=16)
            # ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(xdivision))
            # ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter((max(y) - (min(y)))*100, decimals=1, symbol=''))
            ticks_visual(ax)
            grid_visual(ax)
            if xlimit != 0:
                plt.xlim(xlimit)
            if ylimit != 0:
                plt.ylim(ylimit)
            else:
                # plt.ylim((min(y)), (max(y) * 1.1))
                pass

            if topng:
                fig.savefig(join(self.ppath, ""))

        return data

        # def display_nc_all(self):
        from re import findall
        from os import listdir

        files = listdir(self.bpath)
        for file_name in files:
            numbers = findall(r"\d+", file_name)
            rotation_number = []
            for i in range(len(numbers)):
                if int(numbers[i]) // 5000 != 0:
                    rotation_number.append(numbers[i])
            self.rotationis(rotation_number[0])
            self.display_nc(file_name)

    def display_data(self, data, xlimit=None, ylimit=None, disp=True):
        if not xlimit:
            x = data[1]
            y = data[0]
        else:
            n = self.idx_of_the_nearest(data[1], xlimit)
            x = data[1][n[1] : n[0]]
            y = data[0][n[1] : n[0]]

        if disp:
            # xdivision = 200
            akmp.font_setup(size=28)
            fig = plt.figure(figsize=(16, 9), dpi=50)
            ax = fig.add_subplot(
                1,
                1,
                1,
                xlabel=r"${\rm Wavelength}{\ }{\rm (nm)}$",
                ylabel=r"${\rm Intensity}{\ }{\rm (arb.unit)}$",
            )
            ax.plot(data[1], data[0], ".-")
            # ax.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=0, fontsize=28)
            # ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(xdivision))
            ax.yaxis.set_major_formatter(
                mpl.ticker.PercentFormatter((max(y) - (min(y))) * 100, decimals=1, symbol="")
            )
            akmp.ticks_visual(ax)
            akmp.grid_visual(ax)
            if xlimit:
                plt.xlim(xlimit)
            if ylimit:
                plt.ylim(ylimit)
            else:
                plt.ylim((min(y)), (max(y) * 1.1))

        return data

    def calcgauss(self, data, rangeis, num_gauss=1, par_enable=True):
        n = self.idx_of_the_nearest(data[1], rangeis)
        x = data[1][n[1] : n[0]]
        y = data[0][n[1] : n[0]]
        from lmfit.models import GaussianModel, ConstantModel

        if num_gauss == 1:
            mod = ConstantModel() + GaussianModel()
            params = mod.make_params()
            par_val = {
                "c": min(y),
                "center": x[np.argmax(y)],
                "sigma": 0.005,
                "amplitude": (max(y) - min(y)) / 200,
            }
            par_vary = {
                "c": par_enable,
                "center": par_enable,
                "sigma": par_enable,
                "amplitude": par_enable,
            }
        elif num_gauss == 2:
            mod = ConstantModel() + GaussianModel(prefix="gauss1_") + GaussianModel(prefix="gauss2_")
            params = mod.make_params()
            par_val = {
                "c": min(y),
                "gauss1_center": x[np.argmax(y)],
                "gauss1_sigma": 0.005,
                "gauss1_amplitude": (max(y) - min(y)) / 200,
                "gauss2_center": x[np.argmax(y)],
                # 'gauss2_center' : data[1][np.argmax(data[0])],
                "gauss2_sigma": 0.01,
                "gauss2_amplitude": (max(y) - min(y)) / 400,
            }
            par_vary = {
                "c": par_enable,
                "gauss1_center": par_enable,
                "gauss1_sigma": par_enable,
                "gauss1_amplitude": par_enable,
                "gauss2_center": par_enable,
                "gauss2_sigma": par_enable,
                "gauss2_amplitude": par_enable,
            }
        for name in mod.param_names:
            params[name].set(value=par_val[name], vary=par_vary[name])  # 初期値  # パラメータを動かすかどうか
        self.out = mod.fit(data=y, x=x, params=params)
        return self.out, max(y)

    def gaussian(self, x, amp, cen, wid):
        """1-d gaussian: gaussian(x, amp, cen, wid)"""
        return (amp / (np.sqrt(2 * np.pi) * wid)) * np.exp(-((x - cen) ** 2) / (2 * wid ** 2))

    def display_gaussian(
        self, data, out, rangeis, xlimit=None, ylimit=None, num_gauss=1, subplot=None, fig=None, fontsize=28
    ):
        x2 = np.linspace(data[1][0], data[1][-1], 10000)
        n = self.idx_of_the_nearest(data[1], rangeis)
        x = data[1][n[1] : n[0]]
        y = data[0][n[1] : n[0]]

        akmp.font_setup(size=fontsize)
        if subplot:
            ax = fig.add_subplot(
                subplot[0],
                subplot[1],
                subplot[2],
                xlabel=r"${\rm Wavelength}{\ }{\rm (nm)}$",
                ylabel=r"${\rm Intensity}{\ }{\rm (arb.unit)}$",
            )
        else:
            fig = plt.figure(figsize=(16, 9), dpi=50)
            ax = fig.add_subplot(
                1,
                1,
                1,
                xlabel=r"${\rm Wavelength}{\ }{\rm (nm)}$",
                ylabel=r"${\rm Intensity}{\ }{\rm (arb.unit)}$",
            )
        ax.plot(data[1], data[0] - out.best_values["c"], "o", label=r"Data", c="k")
        if num_gauss == 1:
            ax.plot(
                x2,
                self.gaussian(
                    x2, out.best_values["amplitude"], out.best_values["center"], out.best_values["sigma"]
                ),
                "-",
                label=r"Fitting",
                c="r",
            )
        elif num_gauss == 2:
            ax.plot(
                x2,
                self.gaussian(
                    x2,
                    out.best_values["gauss1_amplitude"],
                    out.best_values["gauss1_center"],
                    out.best_values["gauss1_sigma"],
                ),
                "-",
                label=r"Low temperature",
                c="C1",
            )
            ax.plot(
                x2,
                self.gaussian(
                    x2,
                    out.best_values["gauss2_amplitude"],
                    out.best_values["gauss2_center"],
                    out.best_values["gauss2_sigma"],
                ),
                "-",
                label=r"High temperature",
                c="C2",
            )
            ax.plot(
                x2,
                self.gaussian(
                    x2,
                    out.best_values["gauss1_amplitude"],
                    out.best_values["gauss1_center"],
                    out.best_values["gauss1_sigma"],
                )
                + self.gaussian(
                    x2,
                    out.best_values["gauss2_amplitude"],
                    out.best_values["gauss2_center"],
                    out.best_values["gauss2_sigma"],
                ),
                "-",
                label=r"Summation",
                c="r",
            )
        ax.legend(bbox_to_anchor=(1, 1), loc="upper right", borderaxespad=0)
        ax.xaxis.set_major_locator(mpl.ticker.LinearLocator(3))
        ax.yaxis.set_major_formatter(
            mpl.ticker.PercentFormatter((max(y) - out.best_values["c"]) * 100, decimals=1, symbol="")
        )
        akmp.ticks_visual(ax)
        akmp.grid_visual(ax)
        if xlimit:
            plt.xlim(xlimit)
        if ylimit:
            plt.ylim(ylimit)
        else:
            plt.ylim((min(y)) - out.best_values["c"], (max(y) - out.best_values["c"]) * 1.1)

    def calc_fwhm(
        self,
        fp,
        rangeis=None,
        xlimit=None,
        ylimit=0,
        num_gauss=1,
        disp=True,
        subplot=None,
        fig=None,
        fontsize=28,
    ):
        if type(fp) == str:  # when row nc data is selected
            data = self.convert_nc(fp)
        elif type(fp) != np.ndarray:
            return 'please insert fp="row nc data" or data="converted nc data"'
        else:
            data = fp

        if xlimit is None:
            xlimit = rangeis
        out, intencity = self.calcgauss(data, rangeis, num_gauss=num_gauss)
        if disp:
            self.display_gaussian(
                data,
                out,
                rangeis=rangeis,
                xlimit=xlimit,
                ylimit=ylimit,
                num_gauss=num_gauss,
                subplot=subplot,
                fig=fig,
                fontsize=fontsize,
            )
        if num_gauss == 1:
            if type(out.params["sigma"].stderr) == type(None):
                out.params["sigma"].stderr = 0
            sigma = [[out.params["sigma"].value, out.params["sigma"].stderr]]
            fwhm = 2 * np.array(sigma) * np.sqrt(2 * np.log(2))
            print(f"FWHM {fwhm[0][0]:.4f} +- {fwhm[0][1]:.4f} nm   intencity {intencity}   ", end="")
        elif num_gauss == 2:
            if type(out.params["gauss1_sigma"].stderr) == type(None):
                out.params["gauss1_sigma"].stderr = 0
            if type(out.params["gauss2_sigma"].stderr) == type(None):
                out.params["gauss2_sigma"].stderr = 0
            self.sigma = [
                [out.params["gauss1_sigma"].value, out.params["gauss1_sigma"].stderr],
                [out.params["gauss2_sigma"].value, out.params["gauss2_sigma"].stderr],
            ]
            fwhm = 2 * np.array(self.sigma) * np.sqrt(2 * np.log(2))
            print(
                f"FWHM {fwhm[0][0]:.4f} +- {fwhm[0][1]:.4f} nm and {fwhm[1][0]:.4f} +- {fwhm[1][1]:.4f} nm intencity {intencity}   ",
                end="",
            )
        return fwhm

    def subtract_nc(self, name1, name2):
        data_back = self.convert_nc(name2)
        data_sig = self.convert_nc(name1)

        for i in range(len(data_sig[0])):
            data_sig[0][i] = data_sig[0][i] - data_back[0][i]

        return data_sig

    # def calc_temperature(self, fwhm1, fwhm2, explain = "",A=1.0079):
    #     if len(fwhm1)==2:
    #         deltalam = [(fwhm1[0][0]**2 - fwhm2**2)**0.5, (fwhm1[0][1]**2 - fwhm2**2)**0.5]
    #         atom_temperature = [(deltalam[0] / (7.16e-7 * self.wavelength))**2 * A, (deltalam[1] / (7.16e-7 * self.wavelength))**2 * A]
    #         print(f'{atom_temperature[0]:.2f} K and {atom_temperature[1]:.2f} K   {explain}')
    #     else :
    #         deltalam = (fwhm1**2 - fwhm2**2)**0.5
    #         atom_temperature = (deltalam / (7.16e-7 * self.wavelength))**2 * A
    #         print(f'{atom_temperature:.2f} K    {explain}')
    #     return atom_temperature

    def calc_temperature(self, fwhm1, fwhm2, explain="", A=1.0079):
        if len(fwhm1) == 1:
            fwhm = np.array([fwhm1[0][0], fwhm1[0][0] + fwhm1[0][1], fwhm1[0][0] - fwhm1[0][1]])
            deltalam = (fwhm ** 2 - fwhm2[0][0] ** 2) ** 0.5
            atom_temperature = (deltalam / (7.16e-7 * self.wavelength)) ** 2 * A
            print(
                f"{atom_temperature[0]:.2f} +{atom_temperature[1]-atom_temperature[0]} -{atom_temperature[0]-atom_temperature[2]}  K   {explain}"
            )
        else:
            fwhm = np.array(
                [
                    [fwhm1[0][0], fwhm1[0][0] + fwhm1[0][1], fwhm1[0][0] - fwhm1[0][1]],
                    [fwhm1[1][0], fwhm1[1][0] + fwhm1[1][1], fwhm1[1][0] - fwhm1[1][1]],
                ]
            )
            deltalam = (fwhm ** 2 - fwhm2[0][0] ** 2) ** 0.5
            atom_temperature = (deltalam / (7.16e-7 * self.wavelength)) ** 2 * A
            print(
                f"{atom_temperature[0][0]:.2f} +{atom_temperature[0][1]-atom_temperature[0][0]} -{atom_temperature[0][0]-atom_temperature[0][2]} K and {atom_temperature[1][0]:.2f} +{atom_temperature[1][1]-atom_temperature[1][0]} -{atom_temperature[1][0]-atom_temperature[1][2]} K   {explain}"
            )

    def idx_of_the_nearest(self, data, value):
        if type(value) == float:
            idx = np.argmin(np.abs(np.array(data) - value))
            # print(np.abs(np.array(data) - value))
            return idx
        if type(value) == list:
            idx = [None] * len(value)
            for i in range(len(value)):
                idx[i] = np.argmin(np.abs(np.array(data) - value[i]))
                # idx[i] = [value[i], np.argmin(np.abs(np.array(data) - value[i]))] #としてもよい
                # print(np.abs(np.array(data) - value[i]))
            return idx


def iscd(fp):
    split1 = "\\"
    split2 = "/"
    return len(fp.split(split1)) == 1 and len(fp.split(split2)) == 1

