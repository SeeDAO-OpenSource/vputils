from datetime import datetime, timedelta
import time
import pandas as pd
from binance.spot import Spot
from binance.error import ClientError

class DataFetching(object):
    def __init__(self):
        self.client =Spot()

    # 定义获取 K 线数据的函数
    def get_klines(self, symbol, interval, start_date, end_date, ):
        df=pd.DataFrame()
        end_date_obj = datetime.strptime(end_date, "%Y%m%d")
        next_day = end_date_obj + timedelta(days=1)
        end_date = next_day.strftime("%Y%m%d")
        date_range = pd.date_range(start=start_date,end=end_date,freq="D")

        for d in range(0,len(date_range)):

            if d <= (len(date_range)-2):

                start_date = int(time.mktime(date_range[d].timetuple()) * 1000)
                end_date = int(time.mktime(date_range[d+1].timetuple()) * 1000)

                try:
                    klines = self.client.klines(symbol=symbol, interval=interval,startTime =start_date,endTime=end_date)
                    k_df = pd.DataFrame(
                        klines,
                        columns=[
                            'open_time', 'open', 'high', 'low', 'close', 'volume',
                            'close_time', 'quote_volume', 'number_trades',
                            'taker_buy_base_volume', 'taker_buy_quote_volume', 'unused_filed'
                        ]
                    )
                    df = pd.concat([df, k_df], axis=0)
                except ClientError as e:
                    print(f"ClientError: {e.error_message}")



        return df


    def fetch_data(self,symbol,interval_long,interval_short,start_date,end_date):

        long_term_df = self.get_klines(symbol, interval_long,start_date,end_date)
        short_term_df = self.get_klines(symbol, interval_short,start_date,end_date)

        return long_term_df, short_term_df


if __name__ == '__main__':
    DataFetching = DataFetching().fetch_data('BTCUSDT', '15m', "5m","20240901","20240913")