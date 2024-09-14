import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from .data_plotting import PlottingGraph

import warnings
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)
class DataProcessing():
    def __init__(self):
        self.data_plotting  = PlottingGraph()

    def basic_processing(self,df):

        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms') \
            .dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms') \
            .dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')

        df['time'] = df['open_time'].shift(-1)
        df['time'].iloc[-1] = df['time'].iloc[-2] + (df['time'].iloc[1] - df['time'].iloc[0])
        df.set_index('time', inplace=True)

        df[['open', 'high', 'low', 'close', 'volume']] = df[
            ['open', 'high', 'low', 'close', 'volume']
        ].astype(float)

        return df

    def volume_profile_processing(self, df, profileLevels, ax):
        df.reset_index(inplace=True)
        df['time_num'] = mdates.date2num(df['time'])

        x1, x2 = None, None

        for i in range(len(df)):
            if df['proceed'].iloc[i]:
                x1 = x2
                x2 = i

                if x1 is not None and x2 is not None and x2 > x1:
                    profileLength = x2 - x1
                    priceHighest, priceLowest, tradedVolume = self.get_high_low(df, profileLength, x1)
                    priceStep = (priceHighest - priceLowest) / profileLevels

                    ax = self.data_plotting.plot_pivot_points(df, x1, x2, ax)

                    if priceStep > 0 and profileLength > 0:
                        price_levels = np.linspace(priceLowest, priceHighest, num=profileLevels, endpoint=False)
                        volumeStorageT = np.zeros(len(price_levels))

                        self.compute_volume_distribution(df, x1, profileLength, price_levels, volumeStorageT)

                        ax = self.plot_volume_profile(df, x1, x2, priceLowest, priceHighest, volumeStorageT,
                                                      price_levels, priceStep,ax)

        return ax


    def compute_volume_distribution(self, df, x1, profileLength, price_levels, volumeStorageT):
        for barIndexx in range(profileLength):
            barIndex = x1 + barIndexx
            barPriceHigh = df['high'].iloc[barIndex]
            barPriceLow = df['low'].iloc[barIndex]
            nzVolume = df['volume'].iloc[barIndex]

            price_indices = np.where((price_levels >= barPriceLow) & (price_levels < barPriceHigh))[0]

            for level in price_indices:
                volumeStorageT[level] += nzVolume * (price_levels[1] - price_levels[0]) / (
                    barPriceHigh - barPriceLow if barPriceHigh - barPriceLow != 0 else 1)

    def plot_volume_profile(self, df, x1, x2, priceLowest, priceHighest, volumeStorageT, price_levels,priceStep, ax):
        time_start = df['time_num'].iloc[x1]
        time_end = df['time_num'].iloc[x2 - 1]

        max_volume = volumeStorageT.max()
        norm_volumes = volumeStorageT / max_volume


        ax = self.data_plotting.plot_rectangle(ax, time_start, priceLowest, time_end - time_start,
                                                priceHighest - priceLowest, '#1872df', 0.3)


        levelBelowPoc, levelAbovePoc = self.find_value_area(volumeStorageT, totalVolumeTraded=volumeStorageT.sum())

        for j in range(len(price_levels)):
            vol = norm_volumes[j]
            if vol > 0:
                rect_height = (price_levels[1] - price_levels[0]) * 0.9
                rect_width = (time_end - time_start) * vol * 0.8
                rect_x = time_start
                rect_y = price_levels[j]

                color = '#ffd264' if levelBelowPoc <= j <= levelAbovePoc else '#e3e3e3'
                ax = self.data_plotting.plot_rectangle(ax, rect_x, rect_y, rect_width, rect_height, color, 1)


        ax = self.data_plotting.plot_poc_and_value_area_lines(ax, time_start, time_end, price_levels, levelBelowPoc, levelAbovePoc,priceStep,volumeStorageT)

        return ax

    def find_value_area(self, volumeStorageT, totalVolumeTraded):
        max_volume_index = np.argmax(volumeStorageT)
        valueArea = volumeStorageT[max_volume_index]
        levelAbovePoc, levelBelowPoc = max_volume_index, max_volume_index
        valueAreaThreshold = totalVolumeTraded * 0.68

        while valueArea < valueAreaThreshold:
            if levelBelowPoc == 0 and levelAbovePoc == len(volumeStorageT) - 1:
                break

            volumeAbovePoc = volumeStorageT[levelAbovePoc + 1] if levelAbovePoc < len(volumeStorageT) - 1 else 0
            volumeBelowPoc = volumeStorageT[levelBelowPoc - 1] if levelBelowPoc > 0 else 0

            if volumeAbovePoc >= volumeBelowPoc:
                valueArea += volumeAbovePoc
                levelAbovePoc += 1
            else:
                valueArea += volumeBelowPoc
                levelBelowPoc -= 1

        return levelBelowPoc, levelAbovePoc

    def get_high_low(self,df, length, offset):

        htf_l = df['low'].iloc[offset]
        htf_h = df['high'].iloc[offset]
        vol = 0.0

        for x in range(length):
            htf_l = min(df['low'].iloc[offset + x], htf_l)
            htf_h = max(df['high'].iloc[offset + x], htf_h)
            vol += df['volume'].iloc[offset + x]

        return htf_h, htf_l, vol
    def pivot_high(self,df, length):

        rolling_high = df['high'].rolling(window=2 * length + 1, center=True).max()
        pivot_highs = np.where(df['high'] == rolling_high, df['high'], np.nan)
        return pd.Series(pivot_highs, index=df.index)

    def pivot_low(self,df, length):

        rolling_low = df['low'].rolling(window=2 * length + 1, center=True).min()
        pivot_lows = np.where(df['low'] == rolling_low, df['low'], np.nan)
        return pd.Series(pivot_lows, index=df.index)
