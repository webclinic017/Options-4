from DataDownload import ohlc_update
from market_calls import Market

import numpy as np
import talib as ta
from datetime import datetime


def volatility(ticker,time_frame='1D',days_back=10,override_refresh=True):
    
    market = Market()
    
    main_df = ohlc_update(ticker,time_frame,fresh_download=False)

    last_entry_date = main_df.iloc[-1].name.date()
    if not override_refresh:
        if last_entry_date!=datetime.now().date() or last_entry_date.weekday() not in [5,6]:
            fresh_download = False
        else:
            fresh_download = True
            print("Updating OHLC DataFrame")
            main_df = ohlc_update(ticker,time_frame,fresh_download=fresh_download)

    q = market.quote(ticker)
    
    if not q.lastTradePrice:
        last_price = q.lastTradePrice
    else:
        last_price = main_df.iloc[-1].Close

    df = main_df[['Close']].iloc[-days_back:-1]

    df['deviations'] = np.log(df.Close/df.Close.shift(1))

    df.dropna(inplace=True)

    n = len(df)

    df['variance'] = df.deviations**2
    
    s = (datetime.now() - datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)).total_seconds()
    
    r_last = np.log(last_price/df.iloc[-1].Close)**2
    
    r_1 = df.variance.iloc[0]
    
    r_mid = df.variance[1:-1].sum()
    
    vol_252 = np.sqrt((252/n)*(((86400-s)/86400)*(r_1)+r_mid+r_last))
    
    _atr = ta.ATR(main_df.High,main_df.Low,main_df.Close,14).values[-1]
    
    return vol_252, _atr

if __name__=='__main__':
    ticker = 'SPY'
    time_frame = '1D'
    fresh_download = False
    days_back = 12
    print(volatility(ticker,time_frame,days_back,True))
