#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
import pandas as pd
import datetime
import numpy as np
import multiprocessing
import pandas_ta as ta
from joblib import Parallel,delayed


# In[ ]:






# In[ ]:



def get_crypto_list():
     base_url='https://fapi.binance.com'
     path='/fapi/v1/exchangeInfo'
     r=requests.get(base_url+path)
     j=r.json()

     symbols=j['symbols']
     usdt_symbol=[]
     for symbol in symbols:
        if symbol['symbol'].endswith('USDT'):
            usdt_symbol.append(symbol['symbol'])
     return usdt_symbol


# In[ ]:


def get_candlestick_data(name):
    base_url='https://fapi.binance.com'
    path='/fapi/v1/klines'
    params={'symbol':name,'interval':'1h','limit':1500}
    r=requests.get(base_url+path,params=params)
    j=r.json()
    columns = ['Open_Time', 'Open', 'High', 'Low', 'Close', 'volume']
    data = [candlestick[:6] for candlestick in j]
    df=pd.DataFrame(data,columns=columns)

    df['Open_Time'] = pd.to_datetime(df['Open_Time'], unit='ms')
    #df['Open_Time'] = df['Open_Time'].dt.strftime('%d-%m-%y')
    return df


# In[ ]:
def retrieve_candlestick_data(name):
    try:
        candle = get_candlestick_data(name)
        return (name, candle)
    except Exception as e:
        return (name, f"Error occurred while retrieving data for {name}: {e}")
names=get_crypto_list()
results = Parallel(n_jobs=-1)(delayed(retrieve_candlestick_data)(name) for name in names)

All_crypto_candlestick = {name: candle for name, candle in results if not isinstance(candle, str) and candle is not None}

for name, error in results:
    if isinstance(error, str):
        print(error)




# In[ ]:


All_crypto_candlestick['BTCUSDT']


# In[ ]:



for name,df in All_crypto_candlestick.items():
        df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
        df['High'] = pd.to_numeric(df['High'], errors='coerce')
        df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        if len(df)>15:
                sti=ta.supertrend(df['High'],df['Low'],df['Close'],length=10,multiplier=3)
                last_row=sti['SUPERTd_10_3.0'].iloc[-2]
                second_last_row=sti['SUPERTd_10_3.0'].iloc[-3]
        if second_last_row is not None and last_row != second_last_row:
               print(f"Transition detected in the last row: {second_last_row} -> {last_row}")
               print(name)
               print(df['Open_Time'].iloc[-1])
        else:
                #print(f"No transition detected in the last row: {second_last_row} -> {last_row}")
                #print(name)
                None


# In[ ]:


for name,df in All_crypto_candlestick.items():
        df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
        df['High'] = pd.to_numeric(df['High'], errors='coerce')
        df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        df['ema13'] = ta.ema(df.Close,length=13)
        df['ema25'] = ta.ema(df.Close,length=25)
        df['ema50'] = ta.ema(df.Close,length=50)
        df['rsi']=ta.rsi(df.Close,length=3)
        ema13=df['ema13'].iloc[-1]
        ema25=df['ema25'].iloc[-1]
        ema50=df['ema50'].iloc[-1]
        rsi=df['rsi'].iloc[-2]
        if (rsi<22 and ema13>ema25 and ema25>ema50):
          print(name + ' '+str(rsi) +' buy')
        if (rsi>77 and ema13<ema25 and ema25<ema50):
          print(name + ' '+str(rsi)+ ' sell')


# In[ ]:


print(All_crypto_candlestick['QTUMUSDT'])

