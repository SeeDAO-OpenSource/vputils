import os
import webbrowser
import mpld3
from src.data_fetching import *
from src.data_processing import *
from src.data_plotting import *

import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


class CryptoVP(object):
    def __init__(
        self,
        symbol,
        long_term,
        short_term,
        start_date,
        end_date,
        pvtLength=20,
        profileLevels=25,
    ):
        self.symbol = symbol
        self.long_term = long_term
        self.short_term = short_term
        self.start_date = start_date
        self.end_date = end_date
        self.pvtLength = pvtLength
        self.profileLevels = profileLevels

        self.data_fetcher = DataFetching()
        self.data_processing = DataProcessing()
        self.data_plotting = PlottingGraph()

    def main(self):

        print("正在获取数据···")
        long_df, short_df = self.data_fetcher.fetch_data(
            self.symbol, self.long_term, self.short_term, self.start_date, self.end_date
        )
        print("获取数据成功···")

        print("正在处理数据···")
        long_df, final_df = self.process_crypto_data(long_df, short_df)
        print("处理数据成功···")

        print("正在生成图片···")
        self.plot_crypto_data(long_df, final_df)
        print("生成图片成功···")

    def process_crypto_data(self, long_df, short_df):

        basic_long_df = self.data_processing.basic_processing(long_df)
        basic_short_df = self.data_processing.basic_processing(short_df)
        basic_long_df["pvtHigh"] = self.data_processing.pivot_high(
            basic_long_df, self.pvtLength
        )
        basic_long_df["pvtLow"] = self.data_processing.pivot_low(
            basic_long_df, self.pvtLength
        )

        basic_long_df["proceed"] = (~basic_long_df["pvtHigh"].isna()) | (
            ~basic_long_df["pvtLow"].isna()
        )

        final_df = basic_short_df.join(
            basic_long_df[["pvtHigh", "pvtLow", "proceed"]], how="left"
        )
        final_df["proceed"] = final_df["proceed"].fillna(False)

        return basic_long_df, final_df

    def plot_crypto_data(self, long_df, final_df):

        kline_fig, kline_ax = self.data_plotting.plot_kline_and_volume(long_df)

        self.data_processing.volume_profile_processing(
            final_df, self.profileLevels, kline_ax
        )

        plt.title(
            f"{self.symbol}_{self.long_term}_{self.short_term}_{self.start_date}-{self.end_date}_VP"
        )
        plt.tight_layout()

        html_str = mpld3.fig_to_html(kline_fig)
        html_file = f"{self.symbol}_{self.long_term}_{self.short_term}_{self.start_date}-{self.end_date}_VP.html"
        file_path = os.path.join("output", html_file)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_str)

        url = "file://" + os.path.realpath(file_path)
        webbrowser.open(url)


if __name__ == "__main__":
    # CryptoVP("BTCUSDT", "15m", "15m", "20240905", "20240914").main()

    while True:
        print(
            "请输入以下参数（交易对, 长时间, 短时间, 开始日期, 结束日期），以空格分隔（输入'q'退出）："
        )

        user_input = input(
            "说明：（-短时间 小于等于 长时间；-注意大小写；）\n例如：BTCUSDT 15m 5m 20240901 20240914\n： "
        )
        if user_input.lower() == "q":
            print("退出程序")
            break

        try:
            symbol, interval, long_term, start_date, end_date = user_input.split()
        except ValueError:
            print(
                "输入格式错误，请确保输入格式为：交易对, 长时间, 短时间, 开始日期, 结束日期。"
            )
            continue

        try:
            CryptoVP(symbol, interval, long_term, start_date, end_date).main()
        except Exception as e:
            print(f"发生错误：{e}")

        continue_input = input("是否继续输入参数？(输入 'y' 继续，其他任意键退出)： ")
        if continue_input.lower() != "y":
            print("退出程序")
            break
