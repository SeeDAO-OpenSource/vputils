import numpy as np
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates


class PlottingGraph:
    def __init__(self):
        pass

    def plot_kline_and_volume(self, df):

        candle_df = df.copy()
        candle_df = candle_df[["open", "high", "low", "close", "volume"]]
        candle_df.reset_index(inplace=True)

        candle_df["time_num"] = mdates.date2num(candle_df["time"])

        fig, ax = plt.subplots(figsize=(18, 9))
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FFFFFF")

        candlestick_ohlc(
            ax,
            candle_df[["time_num", "open", "high", "low", "close"]].values,
            width=0.002,
            colorup="#1abc9c",
            colordown="#e74c3c",
            alpha=0.9,
        )

        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.xticks(rotation=45)

        ax.set_xlim(candle_df["time_num"].min(), candle_df["time_num"].max())

        ax.xaxis.set_major_locator(plt.MaxNLocator(20))
        ax.yaxis.set_major_locator(plt.MaxNLocator(20))

        price_min = df["low"].min()
        price_max = df["high"].max() + 500
        volume_height = (price_max - price_min) * 0.2

        ax.set_ylim(price_min - volume_height, price_max)

        candle_df["color"] = np.where(
            candle_df["close"] >= candle_df["open"], "#17a589", "#cb4335"
        )

        volume_base = price_min - volume_height
        volume_scale = volume_height / candle_df["volume"].max()

        for i in range(len(candle_df)):

            time = candle_df["time_num"].iloc[i]
            volume = candle_df["volume"].iloc[i] * volume_scale
            color = candle_df["color"].iloc[i]
            ax.bar(
                time,
                volume,
                bottom=volume_base,
                width=0.002,
                color=color,
                align="center",
            )

        return fig, ax

    def plot_pivot_points(self, df, x1, x2, ax):
        if (
            np.isnan(df["pvtHigh"].iloc[x1])
            and df["pvtHigh"].iloc[x2] > df["pvtLow"].iloc[x1]
        ):
            pvtHigh = df["pvtHigh"].iloc[x2]
            pvtLow = df["pvtLow"].iloc[x1]

            time_pvtLow = df["time_num"].iloc[x1]
            time_pvtHigh = df["time_num"].iloc[x2]

            ax = self.plot_pviot_high_low_point(
                ax, pvtHigh, pvtLow, time_pvtHigh, time_pvtLow
            )
        return ax

    def plot_poc_and_value_area_lines(
        self,
        ax,
        time_start,
        time_end,
        price_levels,
        levelBelowPoc,
        levelAbovePoc,
        priceStep,
        volumeStorageT,
    ):
        rect_value_area_width = time_end - time_start
        y_rect_value_area = price_levels[levelBelowPoc]
        rect_value_area_height = (
            price_levels[levelAbovePoc] - price_levels[levelBelowPoc]
        ) + priceStep
        ax = self.plot_rectangle(
            ax,
            time_start,
            y_rect_value_area,
            rect_value_area_width,
            rect_value_area_height,
            "#1872df",
            0.4,
        )

        ax = self.plot_line(
            ax, price_levels[levelBelowPoc], time_start, time_end, "#1872df", 1
        )
        ax = self.plot_line(
            ax,
            price_levels[levelAbovePoc] + (price_levels[1] - price_levels[0]) * 0.9,
            time_start,
            time_end,
            "#1872df",
            1,
        )

        max_volume_price = (
            price_levels[np.argmax(volumeStorageT)]
            + (price_levels[1] - price_levels[0]) * 0.9 / 2
        )
        ax = self.plot_line(ax, max_volume_price, time_start, time_end, "red", 1)

        return ax

    def plot_pviot_high_low_point(self, ax, pvt_high, pvt_low, high_time, low_time):

        ax.annotate(
            f"{pvt_low:.2f}",
            xy=(high_time, pvt_low),
            fontsize="x-small",
            xytext=(low_time, pvt_low - (pvt_low * 0.002)),
        )

        ax.annotate(
            f" {pvt_high:.2f}",
            xy=(high_time, pvt_high),
            fontsize="x-small",
            xytext=(high_time, pvt_high + (pvt_high * 0.002)),
        )

        return ax

    def plot_rectangle(self, ax, x_0, y_0, x_width, y_hight, color, alphna):

        bg_rect = patches.Rectangle(
            (x_0, y_0),
            width=x_width,
            height=y_hight,
            linewidth=0,
            edgecolor=None,
            facecolor=color,
            alpha=alphna,
        )
        ax.add_patch(bg_rect)

        return ax

    def plot_line(self, ax, y, x_0, x_1, color, width):

        ax.hlines(y=y, xmin=x_0, xmax=x_1, color=color, linestyle="--", linewidth=width)

        return ax
