__doc__ = """	
statutils houses the class which helps with all of the delicate matplotlib plot calls	
=====================================================================================	
Plotting these RV charts requires some nuance and it is best abstracted. Especially	
considering sometimes we want these charts to just be output in a Jupyter notebook,	
or a PyQT5 front end or within a pdf as part of a subset of charts. This class has	
been written to aid with the plotting so whether you are just running prototypes in	
some sort of user interface or you are plotting to a specific axis in a chart grid	
in a pdf output, this class can handle it.	
"""
import log
logger = log.setup('root')
import os

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats
from datetime import datetime


class RGB_colour_picker():
    def __init__(self, r, g, b, increment_size=3):
        self.r = r / 255
        self.g = g / 255
        self.b = b / 255
        self.increment_size = increment_size

    def increment(self, color):
        if color == 'r':
            self.r += self.increment_size/255
        elif color == 'g':
            self.g += self.increment_size/255
        elif color == 'b':
            self.b += self.increment_size/255
    
    def set_increment_size(self, size):
        self.increment_size = size
    
    def get(self):
        return (self.r, self.g, self.b)

class Issuer_line_fig():
    ''' Neatest way to plot the issuer report curves. The main average calculated curve is bold and the 
    constituents are faint/translucent.'''
    def __init__(self, xlabel, ylabel, title, ax_in=None, pngsavepath=''):
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.ax = ax_in
        self.pngsavepath = pngsavepath
        self.b_adj_y_range = False
    
    def set_bold_xy(self, X, y):
        self.bold_X = X
        self.bold_y = y
    
    def set_faint_xy(self, X, y):
        self.faint_X = X
        self.faint_y = y
    
    def set_legend(self, legend_list, isOutsidePlot = False):
        self.legend_list = legend_list
        self.bLegendOutsidePlot = isOutsidePlot
        
    def set_y_axis_range(self, y_min, y_max):
        self.b_adj_y_range = True
        self.y_range_min = y_min
        self.y_range_max = y_max
    
    def plot(self):
        fig, ax = plt.subplots(1,1)
        zorder_param = 2 # To keep bold line always on top
        if isinstance(self.faint_y, list):
            zorder_param = len(self.faint_y) + 1
        
        if self.ax is not None:
            ax = self.ax
        if isinstance(self.bold_X, list) and isinstance(self.bold_y, list):
            if len(self.bold_X) != len(self.bold_y):
                logger.error('X and Y arrays are mismatched - exiting!')
                return
            else:
                for i, item in enumerate(self.bold_X):
                    ax.plot(self.bold_X[i],self.bold_y[i],color='k',linewidth=3,
                            zorder=zorder_param)
        else:
            ax.plot(self.bold_X,self.bold_y,color='k',linewidth=3, zorder=zorder_param)
        
        clr_BBB = RGB_colour_picker(0, 147, 0) # Inc Blue for this one
        clr_AAA = RGB_colour_picker(255, 0, 255) # Inc Green for this one
        clr_AA = RGB_colour_picker(0, 0, 231) # Inc Red for this one
        clr_A = RGB_colour_picker(204, 0, 0) # Inc Green for this one
        if isinstance(self.faint_X, list) and isinstance(self.faint_y, list):
            if len(self.faint_X) != len(self.faint_y):
                logger.error('X and Y arrays are mismatched - exiting!')
                return
            else:
                for i, item in enumerate(self.faint_X, 0):
                    clr = None
                    # We look at the incremented index of the legend_list because
                    # index 0 is always "avg of avg curves". Be very careful about
                    # The ordering. Might need to write a more robust method for this.
                    if '- aaa band' in self.legend_list[i+1].lower():
                        clr = clr_AAA.get()
                        clr_AAA.increment('g')
                    elif '- aa band' in self.legend_list[i+1].lower():
                        clr = clr_AA.get()
                        clr_AA.increment('r')
                    elif '- a band' in self.legend_list[i+1].lower():
                        clr = clr_A.get()
                        clr_A.increment('g')
                    elif '- bbb band' in self.legend_list[i+1].lower():
                        clr = clr_BBB.get()
                        clr_BBB.increment('b')
                    ax.plot(self.faint_X[i],self.faint_y[i],alpha=0.6,color=clr)
        else:
            ax.plot(self.faint_X,self.faint_y,alpha=0.6)
        
        ax.set_title(self.title, fontsize=20)
        ax.set_ylabel(self.ylabel, fontsize=14)
        ax.set_xlabel(self.xlabel, fontsize=14)
        if self.b_adj_y_range:
            ax.set_ylim([self.y_range_max, self.y_range_min])
        if len(self.legend_list) > 0:
            if self.bLegendOutsidePlot:
                ax.legend(self.legend_list, title='Legend', bbox_to_anchor=(0.5, -0.05), loc='upper center', 
                          ncol=2, fontsize=14)
            else:
                ax.legend(self.legend_list,fontsize=10)
        if self.pngsavepath != '':
            plt.savefig(self.pngsavepath)
        return fig
    
class StatUtil():
    ''' Initializing the class:
        
        Parameters
        ----------	
        title_fontsize : int	
            The font size of the chart titles. Defaults to 20.	
        ylabel_fontsize : int	
            The font size of the y axis label. Defaults to 14.	
        xlabel_fontsize : int	
            The font size of the x axis label. Defaults to 14.	
        legend_fontsize : int	
            The font size of the legend text. Defaults to 10.	
    '''
    def __init__(self, *, title_fontsize = 20, ylabel_fontsize = 14, xlabel_fontsize = 14, legend_fontsize = 10):
        self.title_fontsize = title_fontsize
        self.ylabel_fontsize = ylabel_fontsize
        self.xlabel_fontsize = xlabel_fontsize
        self.legend_fontsize = legend_fontsize
    
    
    def get_by_percentile_input(self, y, current_y, percentile_input):
        """
        Returns the percentile value in a series
        Parameters
        ----------
        y : array-like
            An array which contains all the valeus you are looking to compute a mean reverted value from.
        current_y : float
            The current value which will be checked against the y-array's distribution.
        percentile_input : float
            A decimal point value e.g 0.25 == 25%
        Returns
        -------
        mean_reverted_res : float
            The mean reverted value w.r.t where it sits in the distribution.
            It also saves this as a class variable so this is accessible outside of the distplot() func
        """
        return np.percentile(y, percentile_input)
    
    def mean_reversion(self, y, current_y, mean_reversion):
        """
        Returns a mean reverted value w.r.t an array y and a current_y and it's mean_reversion percentage
        value'
        Parameters
        ----------
        y : array-like
            An array which contains all the valeus you are looking to compute a mean reverted value from.
        current_y : float
            The current value which will be checked against the y-array's distribution.
        mean_reversion : float
            A decimal point value which says how much mean reversion to compute e.g 0.25 == 25%
        Returns
        -------
        mean_reverted_res : float
            The mean reverted value w.r.t where it sits in the distribution.
            It also saves this as a class variable so this is accessible outside of the distplot() func
        """
        self.current_percentile = self.percentile(y, current_y)
        if 50 >= self.current_percentile:
            self.mean_reverted_percentile = self.current_percentile + ((50 - self.current_percentile) * mean_reversion)
        else:
            self.mean_reverted_percentile = self.current_percentile - ((self.current_percentile - 50) * mean_reversion)
        self.mean_reverted_value = np.percentile(y, self.mean_reverted_percentile)
        return self.mean_reverted_value
    
    def get_mean_reverted_pct(self):
        return self.mean_reverted_percentile
    
    def get_mean_reverted_value(self):
        return self.mean_reverted_value
    
    def get_current_percentile(self):
        return self.current_percentile
    
    def distplot(self, y, xlabel, ax_in=None, current_y=None, mean_reversion=None, bins=None, title=None):
        ax = ax_in
        if ax is None:
            fig, ax = plt.subplots(1,1)
        sns.distplot(y, axlabel=xlabel, kde=False, ax=ax_in, bins=bins)
        median = np.median(y)
        if current_y is not None:
            ax.axvline(current_y, color='g', linestyle='-', label='Current Value')
            if mean_reversion is not None:
                mean_reverted_res = self.mean_reversion(y, current_y, mean_reversion)
                ax.axvline(mean_reverted_res, color='tab:orange', linestyle='-', label=f'{mean_reversion*100}% Mean Reversion')
        ax.axvline(median, color='r', linestyle='-', label='Median')
        handles, labels = ax.get_legend_handles_labels()
        self.legend_handles = (handles, labels)

    def get_legend_handles(self):
        return self.legend_handles
        
    def boxplot(self, data, positions, ax_in=None, *, mean_reversion_pct_list=None):
        """
        Plot data w.r.t a list of list input
        Parameters
        ----------
        data : List of lists of doubles
            Input data.
        ax_in : matplotlib axis, optional
            The default is None.
        mean_reversion_pct_list : List of Floats, optional
            A list of percentile values which the mean reversion picks out. This will
            be plotted in the violin plots as a horizontal line.
        Returns
        -------
        Fig if no axis passed in.
        """
        fig=None
        ax = ax_in
        if ax is None:
            fig, ax = plt.subplots(1,1)
        quantiles_list = mean_reversion_pct_list if mean_reversion_pct_list is not None else None
        ax.violinplot(data, quantiles=quantiles_list, positions=positions, widths=0.45)
        medians=[]
        for series in data: medians.append(series.median())
        ax.scatter(positions, medians, marker='o', color='royalblue', s=20, zorder=4)
        return fig if ax_in is None else None
    
    def percentile(self, Y_in, current_Y):
        """	
        Get the percentile for a value w.r.t an array excluding itself.	
        
        Parameters	
        ----------	
        Y_in : Numpy Array	
            An array containing all the values you wish to find a percentile value for.	
        current_Y : Double	
            The value which you want to compare to the Y_in values.	
            
        Returns	
        -------	
        Double	
            The percentile value.
        """
        return stats.percentileofscore(Y_in, current_Y)
    
    def plt_scatter(self, X, Y, xlabel, ylabel, title, legend_list, pngsavepath = '', ax_in=None):
        """	
        A text output statistical summary. More useful as a pedagogical tool for the developer	
        to show how this all works than actual production output. Outputs the Quantiles, sd,	
        mean, zscore.	
        
        Parameters	
        ----------	
        title : String	
            Title.	
        X_in : Numpy Array	
            X values array.	
        Y_in : Numpy Array	
            Y values array.	
            
        Returns	
        -------	
        strout : string	
            A long string containing a formatted output of these statistical measures.	
        """
        fig, ax = plt.subplots(1,1)
        if ax_in is not None:
            ax = ax_in
        if isinstance(X, list) and isinstance(Y, list):
            if len(X) != len(Y):
                logger.error('X and Y arrays are mismatched - exiting!')
                return
            else:
                for i, item in enumerate(X):
                    ax.scatter(X[i],Y[i])
        else:
            ax.scatter(X,Y)
        ax.set_title(title, fontsize= self.title_fontsize)
        ax.set_ylabel(ylabel, fontsize = self.ylabel_fontsize)
        ax.set_xlabel(xlabel, fontsize = self.xlabel_fontsize)
        if len(X) > 1:
            if legend_list is not None:
                ax.legend(legend_list, fontsize=self.legend_fontsize)
        if pngsavepath != '':
            plt.savefig(pngsavepath)
        # plt.show()
        return fig if ax_in is None else None
    
    def plt_line_2axis(self, X, Y, xlabel, ylabel, title, legend_list, pngsavepath = '', ax_in=None, **kwargs):
        """	
        A text output statistical summary. More useful as a pedagogical tool for the developer	
        to show how this all works than actual production output. Outputs the Quantiles, sd,	
        mean, zscore.	
        
        Parameters	
        ----------	
        title : String	
            Title.	
        X_in : Numpy Array	
            X values array.	
        Y_in : Numpy Array	
            Y values array.	
            
        Returns	
        -------	
        strout : string	
            A long string containing a formatted output of these statistical measures.	
        """
        fig, ax = plt.subplots(1,1)
        if ax_in is not None:
            ax = ax_in
        if isinstance(X, list) and isinstance(Y, list):
            if len(X) != len(Y):
                logger.error('X and Y arrays are mismatched - exiting!')
                return
            else:
                for i, item in enumerate(X):
                    ax.plot(X[i],Y[i],label=legend_list[i])
        else:
            ax.plot(X,Y,label=legend_list)
        ax.set_title(title, fontsize= self.title_fontsize)
        ax.set_ylabel(ylabel, fontsize = self.ylabel_fontsize)
        ax.set_xlabel(xlabel, fontsize = self.xlabel_fontsize)
        
        # Secondary axis
        sec_X = None
        if 'sec_X' in kwargs:
            sec_X = kwargs['sec_X']
        sec_y = None
        if 'sec_y' in kwargs:
            sec_y = kwargs['sec_y']
        sec_axis_title = None
        if 'sec_axis_title' in kwargs:
            sec_axis_title = kwargs['sec_axis_title']
        sec_legend = None
        if 'sec_legend' in kwargs:
            sec_legend = kwargs['sec_legend']
        if (sec_X is not None) and (sec_y is not None) and (sec_axis_title is not None):
            ax2 = ax.twinx()
            ax2.set_ylabel(sec_axis_title)
            ax2.plot(sec_X, sec_y, color='orange', label=sec_legend)
            ax2.tick_params(axis='y')
        if legend_list is not None and sec_legend is not None:
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2)
        if pngsavepath != '':
            plt.savefig(pngsavepath)
        # plt.show()
        return fig if ax_in is None else None
    
    def plt_line(self, X, Y, xlabel, ylabel, title, legend_list=None, pngsavepath = '', ax_in=None, **kwargs):
        fig, ax = plt.subplots(1,1)
        if ax_in is not None:
            ax = ax_in
        if isinstance(X, list) and isinstance(Y, list):
            if len(X) != len(Y):
                logger.error('X and Y arrays are mismatched - exiting!')
                return
            else:
                for i, item in enumerate(X):
                    ax.plot(X[i],Y[i])
        else:
            ax.plot(X,Y)
        ax.set_title(title, fontsize= self.title_fontsize)
        ax.set_ylabel(ylabel, fontsize = self.ylabel_fontsize)
        ax.set_xlabel(xlabel, fontsize = self.xlabel_fontsize)
        if legend_list is not None:
            ax.legend(legend_list, fontsize=self.legend_fontsize)
        if pngsavepath != '':
            plt.savefig(pngsavepath)
        # plt.show()
        return fig if ax_in is None else None
    
    def stat_summary(self, title, X_in, Y_in):
        """	
        A text output statistical summary. More useful as a pedagogical tool for the developer	
        to show how this all works than actual production output. Outputs the Quantiles, sd,	
        mean, zscore.	
        
        Parameters	
        ----------	
        title : String	
            Title.	
        X_in : Numpy Array	
            X values array.	
        Y_in : Numpy Array	
            Y values array.	
            
        Returns	
        -------	
        strout : string	
            A long string containing a formatted output of these statistical measures.	
        """
        current_Y = Y_in.iloc[-1]
        strout = '---------------------------------------------------\n'
        strout += (f'Statistical Summary\n{title}:\nCurrent {X_in.name} [{X_in.iloc[-1]}] has value [{current_Y}]\n\n')
        quantile25 = np.quantile(Y_in,.25)
        quantile50 = np.quantile(Y_in,.5)
        quantile75 = np.quantile(Y_in,.75)
        quantile100 = np.quantile(Y_in,1)
        strout += ('Quantiles\nQ1 Quantile [{}]\nQ2 Quantile [{}]\nQ3 Quantile [{}]\nQ4 Quantile [{}]\n'.format(
            quantile25, quantile50, quantile75, quantile100))
        quantiles = [quantile25,quantile50,quantile75,quantile100]
        quantile_count = 1
        for quantile in quantiles:
            if current_Y < quantile:
                strout += (f'Current Y {[current_Y]} lies in Q{quantile_count}\n\n')
                break
            quantile_count += 1
        strout += ('Percentile of current Y value {} is : [{}]\n'.format(
            current_Y, stats.percentileofscore(Y_in, current_Y)))
        sd = np.std(Y_in)
        mean = np.mean(Y_in)
        zscore = (current_Y - mean) / sd
        strout += f'Std Dev of Data : [{sd}]\nMean of Data : [{mean}]\nCurrent Y [{current_Y}] Z-Score : [{zscore}]\n'
        strout += '---------------------------------------------------'
        return strout
    
    # Converts a list of list of coeffs into fitted curves. Must supply legend if >1
    def plot_coeffs_line(self, coeffs_listoflist, curvename_list, X_max, pngsavepath = '', ax_in=None, title_override_name = None, spread_coeffs_list = None):
        """	
        Plot fitted lines with the underlying scatter points preserved (including outliers which are plotted	
        in a different colour))	
    
        Parameters	
        ----------	
        coeffs_listoflist : List of lists of coeffs	
            A list of list of coefficients. So a list of lists of doubles. These coefficients are converted to fitted curves.	
        curvename_list : List	
            list of curvesnames used for the legend. Must supply if > 1.	
        X_scatter : Numpy Array	
            X values in an array.	
        Y_scatter : Numpy Array	
            Y values in an array.	
        X_max : Double	
            The maximum X value you will have the X axis go out to. Heplful to limit extrapolation for most curves.	
        pngsavepath : String, optional	
            The save path of the image if you wish to save a standalone image. The default is ''.	
        ax_in : matplotlib.axis, optional	
            The axis object you wish to plot to. Useful for pdf outputs else leave blank. The default is None.	
        title_override_name : String, optional	
            Title name. The default is None.	
        spread_coeffs_list : List of lists of coeffs optional	
            If you want to calculate spreads to a specific curve you can pass that other curve's coefficients here.	
            The default is None.	
        X_outlier : Numpy Array, optonal.	
            X values in an array. The default is None.	
        Y_outlier : Numpy Array, optonal.	
            Y values in an array. The default is None.	
            
        Returns	
        -------	
        matplotlib.figure	
            Returns a figure object, useful for PyQT5 front end which can use this fig object.	
        """
        if len(coeffs_listoflist) != len(curvename_list):
            logger.error(f'Curvename list dimension [{len(curvename_list)}] must equal coeffs dimension [{len(coeffs_listoflist)}]')
            return            
        fig, ax = plt.subplots(1,1)
        if ax_in is not None:
            ax = ax_in
        X = np.linspace(0,X_max,50)
        Y = []
        for coeffs in coeffs_listoflist:
            fit_coeffsline = lambda x: coeffs[0] + x*coeffs[1] + x**2 * coeffs[2] + x**3 * coeffs[3]
            vfunc = np.vectorize(fit_coeffsline)
            Y.append(vfunc(X))
        
        if spread_coeffs_list is not None:
            Y_other = []
            fit_spreadcoeffsline = lambda x: spread_coeffs_list[0] + x*spread_coeffs_list[1] + x**2 * spread_coeffs_list[2] + x**3 * spread_coeffs_list[3]
            vfunc = np.vectorize(fit_spreadcoeffsline)
            Y_other.append(vfunc(X))
            b_tsyfound = False
            Y_spread = []
            for i, curve in enumerate(Y):
                if curvename_list[i] == 'Treasury':
                    b_tsyfound = True
                    continue
                diff = curve - Y_other
                Y_spread.append(diff.transpose())
            if b_tsyfound:
                curvename_list.remove('Treasury')
            Y = Y_spread
            X = X.reshape(-1,1)
        
        if title_override_name is not None:
            ax.set_title(title_override_name, fontsize = self.title_fontsize)
        else:
            ax.set_title('Fitted Yields vs Modified Duration', fontsize = self.title_fontsize)
        ylabel = 'Yield' if spread_coeffs_list is None else 'Spread'
        ax.set_ylabel( ylabel, fontsize = self.ylabel_fontsize)
        ax.set_xlabel('Modified Duration', fontsize = self.xlabel_fontsize)
        
        for i, item in enumerate(Y):
            ax.plot(X,Y[i])
        if len(Y) > 1:
            ax.legend(curvename_list, fontsize=self.legend_fontsize)
        if pngsavepath != '':
            plt.savefig(pngsavepath)
        
        return fig if ax_in is None else None
    
    # Converts a list of list of coeffs into fitted curves. Must supply legend if >1
    def plot_coeffs_line_with_scatter(self, coeffs_listoflist, curvename_list, X_scatter, Y_scatter, X_max, pngsavepath = '', ax_in=None,
                                      title_override_name = None, spread_coeffs_list = None, X_outlier = None, Y_outlier = None):
        """	
        Plot fitted lines with the underlying scatter points preserved (including outliers which are plotted	
        in a different colour))	
    
        Parameters	
        ----------	
        coeffs_listoflist : List of lists of coeffs	
            A list of list of coefficients. So a list of lists of doubles. These coefficients are converted to fitted curves.	
        curvename_list : List	
            list of curvesnames used for the legend. Must supply if > 1.	
        X_scatter : Numpy Array	
            X values in an array.	
        Y_scatter : Numpy Array	
            Y values in an array.	
        X_max : Double	
            The maximum X value you will have the X axis go out to. Heplful to limit extrapolation for most curves.	
        pngsavepath : String, optional	
            The save path of the image if you wish to save a standalone image. The default is ''.	
        ax_in : matplotlib.axis, optional	
            The axis object you wish to plot to. Useful for pdf outputs else leave blank. The default is None.	
        title_override_name : String, optional	
            Title name. The default is None.	
        spread_coeffs_list : List of lists of coeffs optional	
            If you want to calculate spreads to a specific curve you can pass that other curve's coefficients here.	
            The default is None.	
        X_outlier : Numpy Array, optonal.	
            X values in an array. The default is None.	
        Y_outlier : Numpy Array, optonal.	
            Y values in an array. The default is None.	
            
        Returns	
        -------	
        matplotlib.figure	
            Returns a figure object, useful for PyQT5 front end which can use this fig object.	
        """
        if isinstance(curvename_list, list):
            if len(coeffs_listoflist) != len(curvename_list):
                logger.error(f'Curvename list dimension [{len(curvename_list)}] must equal coeffs dimension [{len(coeffs_listoflist)}]')
                return            
        fig, ax = plt.subplots(1,1)
        if ax_in is not None:
            ax = ax_in
        X = np.linspace(0,X_max,50)
        Y = []
        for coeffs in coeffs_listoflist:
            fit_coeffsline = lambda x: coeffs[0] + x*coeffs[1] + x**2 * coeffs[2] + x**3 * coeffs[3]
            vfunc = np.vectorize(fit_coeffsline)
            Y.append(vfunc(X))
        
        if spread_coeffs_list is not None:
            Y_other = []
            fit_spreadcoeffsline = lambda x: spread_coeffs_list[0] + x*spread_coeffs_list[1] + x**2 * spread_coeffs_list[2] + x**3 * spread_coeffs_list[3]
            vfunc = np.vectorize(fit_spreadcoeffsline)
            Y_other.append(vfunc(X))
            b_tsyfound = False
            Y_spread = []
            for i, curve in enumerate(Y):
                if curvename_list[i] == 'Treasury':
                    b_tsyfound = True
                    continue
                diff = curve - Y_other
                Y_spread.append(diff.transpose())
            if b_tsyfound:
                curvename_list.remove('Treasury')
            Y = Y_spread
            X = X.reshape(-1,1)
        
        if title_override_name is not None:
            ax.set_title(title_override_name, fontsize = self.title_fontsize)
        else:
            ax.set_title('Fitted Yields vs Modified Duration', fontsize = self.title_fontsize)
        ylabel = 'Yield' if spread_coeffs_list is None else 'Spread'
        ax.set_ylabel( ylabel, fontsize = self.ylabel_fontsize)
        ax.set_xlabel('Modified Duration', fontsize = self.xlabel_fontsize)
        
        for i, item in enumerate(Y):
            ax.plot(X,Y[i])
        if len(Y) > 1:
            ax.legend(curvename_list, fontsize=self.legend_fontsize)
        for i, item in enumerate(X_scatter):
            ax.scatter(X_scatter[i],Y_scatter[i], s=25)
        if X_outlier is not None and Y_outlier is not None:
            ax.scatter(X_outlier[i], Y_outlier[i], color='r', s=25 )
        if pngsavepath != '':
            plt.savefig(pngsavepath)
        
        return fig if ax_in is None else None
    
    # The first set of coeffs will be a line chart, the rest of the coeffs will be just the scatter points.
    def plot_single_coeffs_line_with_other_scatter(self, coeffs_listoflist, curvename_list, X_scatter, Y_scatter, X_max, pngsavepath = '', ax_in=None,
                                      title_override_name = None, spread_coeffs_list = None, X_outlier = None, Y_outlier = None):
        """	
        Plot fitted lines with the underlying scatter points preserved (including outliers which are plotted	
        in a different colour)) The first curve is plotted as a line chart and the rest are scatter plots.	
    
        Parameters	
        ----------	
        coeffs_listoflist : List of lists of coeffs	
            A list of list of coefficients. So a list of lists of doubles. These coefficients are converted to fitted curves.	
        curvename_list : List	
            list of curvesnames used for the legend. Must supply if > 1.	
        X_scatter : Numpy Array	
            X values in an array.	
        Y_scatter : Numpy Array	
            Y values in an array.	
        X_max : Double	
            The maximum X value you will have the X axis go out to. Heplful to limit extrapolation for most curves.	
        pngsavepath : String, optional	
            The save path of the image if you wish to save a standalone image. The default is ''.	
        ax_in : matplotlib.axis, optional	
            The axis object you wish to plot to. Useful for pdf outputs else leave blank. The default is None.	
        title_override_name : String, optional	
            Title name. The default is None.	
        spread_coeffs_list : List of lists of coeffs optional	
            If you want to calculate spreads to a specific curve you can pass that other curve's coefficients here.	
            The default is None.	
        X_outlier : Numpy Array, optonal.	
            X values in an array. The default is None.	
        Y_outlier : Numpy Array, optonal.	
            Y values in an array. The default is None.	
            
        Returns	
        -------	
        matplotlib.figure	
            Returns a figure object, useful for PyQT5 front end which can use this fig object.	
        """
        if isinstance(curvename_list, list):
            if len(coeffs_listoflist) != len(curvename_list):
                logger.error(f'Curvename list dimension [{len(curvename_list)}] must equal coeffs dimension [{len(coeffs_listoflist)}]')
                return            
        fig, ax = plt.subplots(1,1)
        if ax_in is not None:
            ax = ax_in
        X = np.linspace(0,X_max,50)
        Y = []
        for coeffs in coeffs_listoflist:
            fit_coeffsline = lambda x: coeffs[0] + x*coeffs[1] + x**2 * coeffs[2] + x**3 * coeffs[3]
            vfunc = np.vectorize(fit_coeffsline)
            Y.append(vfunc(X))
        
        if spread_coeffs_list is not None:
            Y_other = []
            fit_spreadcoeffsline = lambda x: spread_coeffs_list[0] + x*spread_coeffs_list[1] + x**2 * spread_coeffs_list[2] + x**3 * spread_coeffs_list[3]
            vfunc = np.vectorize(fit_spreadcoeffsline)
            Y_other.append(vfunc(X))
            b_tsyfound = False
            Y_spread = []
            for i, curve in enumerate(Y):
                if curvename_list[i] == 'Treasury':
                    b_tsyfound = True
                    continue
                diff = curve - Y_other
                Y_spread.append(diff.transpose())
            if b_tsyfound:
                curvename_list.remove('Treasury')
            Y = Y_spread
            X = X.reshape(-1,1)
        
        if title_override_name is not None:
            ax.set_title(title_override_name, fontsize = self.title_fontsize)
        else:
            ax.set_title('Fitted Yields vs Modified Duration', fontsize = self.title_fontsize)
        ylabel = 'Yield' if spread_coeffs_list is None else 'Spread'
        ax.set_ylabel( ylabel, fontsize = self.ylabel_fontsize)
        ax.set_xlabel('Modified Duration', fontsize = self.xlabel_fontsize)
        
        for i, item in enumerate(Y):
            if i == 0:ax.plot(X,Y[i],color='lightslategrey')
        for i, item in enumerate(X_scatter):
            if i > 0: ax.scatter(X_scatter[i],Y_scatter[i], s=25)
        if X_outlier is not None and Y_outlier is not None:
            ax.scatter(X_outlier[i], Y_outlier[i], color='r', s=25 )
        ax.legend(curvename_list, fontsize=self.legend_fontsize)
        if pngsavepath != '':
            plt.savefig(pngsavepath)
        
        return fig if ax_in is None else None
    
    # Returns a fig which can be saved using the .savefig() call found in the PdfPages() class
    def text_to_pdf(self, str_in):
        """	
        Allows you to plot text into a matplotlib.axis object.	
        Returns a fig object which can be saved using the .savefig() call found in the PdfPages() class	
        
        Parameters	
        ----------	
        str_in : String	
            The formatted string you wish to plot in a chart object.	
            
        Returns	
        -------	
        fig : matplotlib.figure	
            The figure object you wish to write this string into.	
        """
        fig = plt.figure(figsize=(11.69,8.27))
        fig.clf()
        txt = str_in
        fig.text(0.1,0.25,txt, transform=fig.transFigure, size=18)
        return fig
    
    def df_to_heatmap(self, df, title=None, outfile='', out_format='.3g',
                      ax_in=None, hide_axis_titles=False,kwargs={}):
        """	
        Plots a DataFrame as a heatmap.	
        
        Parameters	
        ----------	
        df : Pandas.DataFrame	
            The DataFrame you wish to plot to a heatmap. Must only contain doubles.	
            Passing strings as part of the DataFrame will throw arcane errors.	
        title : String	
            The chart title.	
        outfile : String, optional	
            The file path to where you wish to save the image of the chart. The default is ''.	
        out_format : string, optional	
            The formatting of the actual values within the heatmap. The default is '.3g'.	
        ax_in : matplotlib.axis, optional	
            The axis object you wish to plot to. Useful for pdf outputs else leave blank. The default is None.	
            
        Returns	
        -------	
        matplotlib.figure	
            Returns a figure object, useful for PyQT5 front end which can use this fig object.	
        """
        fig, ax = plt.subplots(1,1)
        if ax_in is not None:
            ax = ax_in
        # cmap='RdBu_r' - This is what I used as a default color pre-abstraction
        cmapval = sns.diverging_palette(15, 150, as_cmap=True)
        g = sns.heatmap(df, annot=True, fmt=out_format, ax=ax, cbar=False,
                    cmap=cmapval, **kwargs)
        g.set_yticklabels(g.get_yticklabels(), rotation = 0)
        ax.xaxis.tick_top()
        ax.set_title(title)
        ax.figure.tight_layout()
        if hide_axis_titles:
            ax.set_ylabel('')
            ax.set_xlabel('')
        if outfile != '':
            plt.savefig(outfile)
        return fig if ax_in is None else None