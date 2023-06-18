import pandas as pd
import pandas_ta as ta
import yfinance as yf
import yahoo_fin.stock_info as si
import time

# tickers

tickers = ['^GSPC','^IXIC'] 
sp500 = si.tickers_sp500()
tickers = tickers + sp500

''' para pruebas cambio de tickers a 5 tickers'''
#tickers = tickers[:5]
''''''


# Descargamos datos
close = yf.download(tickers, period='1y', interval='1d')['Adj Close']
close = close.fillna(method='ffill')
time.sleep(.5)

high = yf.download(tickers, period='1y', interval='1d')['High']
high = high.fillna(method='ffill')
time.sleep(.5)

low = yf.download(tickers, period='1y', interval='1d')['Low']
low = low.fillna(method='ffill')
time.sleep(.5)

open = yf.download(tickers, period='1y', interval='1d')['Open']
open = open.fillna(method='ffill')
time.sleep(.5)

volume = yf.download(tickers, period='1y', interval='1d')['Volume']
volume = volume.fillna(method='ffill')

returns = close.pct_change().dropna()


# creamos el dataframe de señales con los tickers como indice
signals = pd.DataFrame(index=tickers)

# Segimiento de indicadores que vamos añadiendo
total_indicators = 0


''' Buscamos y añadimos señales'''


''' Señales de volumen (3)'''

# calculamos si el volumen del ultimo dia supera una vesviacion estandar
signals['vol_1std'] = volume.iloc[-1] > volume.iloc[-1].std()

# Calculamos si el volumen del ultimo dia supera dos veces la desviacion estandar
signals['vol_2std'] = volume.iloc[-1] > volume.iloc[-1].std() * 2

# Calculamos si el volumen del ultimo dia supera tres veces la desviacion estandar
signals['vol_3std'] = volume.iloc[-1] > volume.iloc[-1].std() * 3

total_indicators += 3

''' Señales de rendimiento (3)'''

# calculamos si el rendimiento del ultimo dia supera una vesviacion estandar por arriba o por abajo  
signals['ret_1std'] = returns.iloc[-1] > returns.iloc[-1].std()

# Calculamos si el rendimiento del ultimo dia supera dos veces la desviacion estandar por arriba o por abajo  
signals['ret_2std'] = returns.iloc[-1] > returns.iloc[-1].std() * 2

# Calculamos si el rendimiento del ultimo dia supera tres veces la desviacion estandar por arriba o por abajo  
signals['ret_3std'] = returns.iloc[-1] > returns.iloc[-1].std() * 3

total_indicators += 3

''' Señales de salida de zona de sobrecompra o sobreventa del RSI (2)'''
rsi_period = 14
rsi_high = 70
rsi_low = 30

# para cada ticker:
for ticker in tickers:
    # calculamos el RSI
    rsi = ta.rsi(close[ticker], length=rsi_period)

    # calculamos si el rsi cruza al alza el nivel de sobreventa para añadir la señal true o false en la columna 'RSI_Up' en el indice del ticker correspondiente
    signals.loc[ticker, 'RSI_Up'] = (rsi.iloc[-2] < rsi_low) & (rsi.iloc[-1] > rsi_low)
    # calculamos si el rsi cruza a la baja el nivel de sobrecompra para añadir la señal true o false en la columna 'RSI_Down' en el indice del ticker correspondiente
    signals.loc[ticker, 'RSI_Down'] = (rsi.iloc[-2] > rsi_high) & (rsi.iloc[-1] < rsi_high)

total_indicators += 2


''' Señales del MACD (2)'''
macd_fast = 12
macd_slow = 26
macd_signal = 9

# para cada ticker:
for ticker in tickers:
    # calculamos el MACD
    macd = ta.macd(close[ticker], fast=macd_fast, slow=macd_slow, signal=macd_signal)

    # calculamos si el macd cruza a la baja el nivel de sobrecompra para añadir la señal true o false en la columna 'MACD_Down' en el indice del ticker correspondiente
    signals.loc[ticker, 'MACD__Histo_Down'] = (macd['MACDh_12_26_9'].iloc[-2] > macd['MACDh_12_26_9'].iloc[-1])
    # calculamos si el macd cruza al alza el nivel de sobreventa para añadir la señal true o false en la columna 'MACD_Up' en el indice del ticker correspondiente
    signals.loc[ticker, 'MACD__Histo_Up'] = (macd['MACDh_12_26_9'].iloc[-2] < macd['MACDh_12_26_9'].iloc[-1])

    # calculamos si la linea de señal cruza a la baja la linea del macd para añadir la señal true o false en la columna 'MACD_Signal_Down' en el indice del ticker correspondiente
    signals.loc[ticker, 'MACD_Signal_Up'] = (macd['MACDs_12_26_9'].iloc[-2] > macd['MACD_12_26_9'].iloc[-2]) & (macd['MACDs_12_26_9'].iloc[-1] < macd['MACD_12_26_9'].iloc[-1])
    # calculamos si la linea de señal cruza al alza la linea del macd para añadir la señal true o false en la columna 'MACD_Signal_Up' en el indice del ticker correspondiente
    signals.loc[ticker, 'MACD_Signal_Down'] = (macd['MACDs_12_26_9'].iloc[-2] < macd['MACD_12_26_9'].iloc[-2]) & (macd['MACDs_12_26_9'].iloc[-1] > macd['MACD_12_26_9'].iloc[-1])

total_indicators += 2


''' Señales de desviacion std del ATR(3)'''
atr_period = 14
# para cada ticker:
for ticker in tickers:
    # calculamos el ATR
    atr = ta.atr(high[ticker], low[ticker], close[ticker], length=atr_period)

    # calculamos si el ATR supera una vesviacion estandar para añadir la señal true o false en la columna 'ATR_1std' en el indice del ticker correspondiente
    signals.loc[ticker, 'ATR_1std'] = atr.iloc[-1] > atr.iloc[-1].std()
    # calculamos si el ATR supera dos veces la desviacion estandar para añadir la señal true o false en la columna 'ATR_2std' en el indice del ticker correspondiente
    signals.loc[ticker, 'ATR_2std'] = atr.iloc[-1] > atr.iloc[-1].std() * 2
    # calculamos si el ATR supera tres veces la desviacion estandar para añadir la señal true o false en la columna 'ATR_3std' en el indice del ticker correspondiente
    signals.loc[ticker, 'ATR_3std'] = atr.iloc[-1] > atr.iloc[-1].std() * 3

total_indicators += 3


''' Señales de cruces de medias moviles exponenciales(6)'''
# para cada ticker:
for ticker in tickers:
    # calculamos las medias moviles exponenciales
    ema_12 = ta.ema(close[ticker], length=12)
    ema_26 = ta.ema(close[ticker], length=26)
    ema_50 = ta.ema(close[ticker], length=50)
    ema_100 = ta.ema(close[ticker], length=100)
    ema_200 = ta.ema(close[ticker], length=200)

    # calculamos si la media movil exponencial de 12 cruza a la baja la media movil exponencial de 26 para añadir la señal true o false en la columna 'EMA_12_26_Down' en el indice del ticker correspondiente
    signals.loc[ticker, 'EMA_12_26_Down'] = (ema_12.iloc[-2] > ema_26.iloc[-2]) & (ema_12.iloc[-1] < ema_26.iloc[-1])
    # calculamos si la media movil exponencial de 12 cruza al alza la media movil exponencial de 26 para añadir la señal true o false en la columna 'EMA_12_26_Up' en el indice del ticker correspondiente
    signals.loc[ticker, 'EMA_12_26_Up'] = (ema_12.iloc[-2] < ema_26.iloc[-2]) & (ema_12.iloc[-1] > ema_26.iloc[-1])

    # calculamos si la media movil exponencial de 26 cruza a la baja la media movil exponencial de 50 para añadir la señal true o false en la columna 'EMA_26_50_Down' en el indice del ticker correspondiente
    signals.loc[ticker, 'EMA_26_50_Down'] = (ema_26.iloc[-2] > ema_50.iloc[-2]) & (ema_26.iloc[-1] < ema_50.iloc[-1])
    # calculamos si la media movil exponencial de 26 cruza al alza la media movil exponencial de 50 para añadir la señal true o false en la columna 'EMA_26_50_Up' en el indice del ticker correspondiente
    signals.loc[ticker, 'EMA_26_50_Up'] = (ema_26.iloc[-2] < ema_50.iloc[-2]) & (ema_26.iloc[-1] > ema_50.iloc[-1])

    # calculamos si la media movil exponencial de 50 cruza a la baja la media movil exponencial de 100 para añadir la señal true o false en la columna 'EMA_50_100_Down' en el indice del ticker correspondiente
    signals.loc[ticker, 'EMA_50_100_Down'] = (ema_50.iloc[-2] > ema_100.iloc[-2]) & (ema_50.iloc[-1] < ema_100.iloc[-1])
    # calculamos si la media movil exponencial de 50 cruza al alza la media movil exponencial de 100 para añadir la señal true o false en la columna 'EMA_50_100_Up' en el indice del ticker correspondiente
    signals.loc[ticker, 'EMA_50_100_Up'] = (ema_50.iloc[-2] < ema_100.iloc[-2]) & (ema_50.iloc[-1] > ema_100.iloc[-1])

    # calculamos si la media movil exponencial de 100 cruza a la baja la media movil exponencial de 200 para añadir la señal true o false en la columna 'EMA_100_200_Down' en el indice del ticker correspondiente
    signals.loc[ticker, 'EMA_100_200_Down'] = (ema_100.iloc[-2] > ema_200.iloc[-2]) & (ema_100.iloc[-1] < ema_200.iloc[-1])
    # calculamos si la media movil exponencial de 100 cruza al alza la media movil exponencial de 200 para añadir la señal true o false en la columna 'EMA_100_200_Up' en el indice del ticker correspondiente
    signals.loc[ticker, 'EMA_100_200_Up'] = (ema_100.iloc[-2] < ema_200.iloc[-2]) & (ema_100.iloc[-1] > ema_200.iloc[-1])

    # calculamos el cruce de la muerte de la media movil exponencial de 12, 26, 50 para añadir la señal true o false en la columna 'EMA_Death_Cross_Down_12-26-50' en el indice del ticker correspondiente
    signals.loc[ticker, 'EMA_Death_Cross_Down_12-26-50'] = (ema_12.iloc[-1] < ema_26.iloc[-1]) & (ema_26.iloc[-1] < ema_50.iloc[-1])
    # calculamos el cruce de oro de la media movil exponencial de 12, 26, 50 para añadir la señal true o false en la columna 'EMA_Golden_Cross_Up_12-26-50' en el indice del ticker correspondiente
    signals.loc[ticker, 'EMA_Golden_Cross_Up_12-26-50'] = (ema_12.iloc[-1] > ema_26.iloc[-1]) & (ema_26.iloc[-1] > ema_50.iloc[-1])

    # calculamos el cruce de la muerte de la media movil exponencial de 50, 100, 200 para añadir la señal true o false en la columna 'EMA_Death_Cross_Down_50-100-200' en el indice del ticker correspondiente
    signals.loc[ticker, 'EMA_Death_Cross_Down_50-100-200'] = (ema_50.iloc[-1] < ema_100.iloc[-1]) & (ema_100.iloc[-1] < ema_200.iloc[-1])
    # calculamos el cruce de oro de la media movil exponencial de 50, 100, 200 para añadir la señal true o false en la columna 'EMA_Golden_Cross_Up_50-100-200' en el indice del ticker correspondiente
    signals.loc[ticker, 'EMA_Golden_Cross_Up_50-100-200'] = (ema_50.iloc[-1] > ema_100.iloc[-1]) & (ema_100.iloc[-1] > ema_200.iloc[-1])

total_indicators += 6


''' Señales Donchian Channel (1)'''
Don_Chanel_poeriod = 20
for ticker in tickers:
    # calculamos el canal superior de donchian para añadir la señal true o false en la columna 'Don_Chanel_Up' en el indice del ticker correspondiente
    signals.loc[ticker, 'Don_Chanel_Up'] = (high[ticker].iloc[-Don_Chanel_poeriod:].max() == high[ticker].iloc[-1])
    # calculamos el canal inferior de donchian para añadir la señal true o false en la columna 'Don_Chanel_Down' en el indice del ticker correspondiente
    signals.loc[ticker, 'Don_Chanel_Down'] = (low[ticker].iloc[-Don_Chanel_poeriod:].min() == low[ticker].iloc[-1])

total_indicators += 1




'''Screener'''

# creamos el dataframe screener 
screener = pd.DataFrame(columns=['Signals', 'Score'])

# Concatenamos a Screener el df signals con las filas que tengan al menos una señal
screener = pd.concat([screener, signals[(signals != 0).any(axis=1)].astype(bool)])

# añadimos la puntuación en la columna 'score' para cada ticker que será la suma de las señales que tenga activas en relación al total de señales que se pueden dar
screener['Score'] = (round(signals.sum(axis=1) / total_indicators * 100)).astype(int)

# ordenamos el DataFrame por la columna 'Score' de mayor a menor
screener = screener.sort_values(by='Score', ascending=False)

# Añadimos en la columna 'Signals' el numero de señales que tiene activas cada ticker
n_signals = signals.astype(bool).sum(axis=1)
screener['Signals'] = n_signals.astype(str) + '/' + str(total_indicators)

# calculamos cual es la accion que tiene mas señales activas
max_signals = screener['Signals'].str.split('/', expand=True)[0].astype(int).max()
# creamos un DataFrame vacio con tantas columnas como max_signals + 2 columnas extras. Nombramos esas columnas como  Signals, Score, Signals_1, Signals_2, etc
screener_show = pd.DataFrame(index = screener.index, columns=['Signals', 'Score'] + ['Signals_' + str(i) for i in range(1, max_signals + 1)])

# rellenamos el dataframe screener_show con los datos del dataframe screener
for ticker in screener_show.index:
    print(ticker, screener.loc[ticker, 'Signals'], screener.loc[ticker, 'Score'], signals.loc[ticker, signals.loc[ticker] == True].index.values)
    # En el DataFrame screener_show añadimos una fila con el ticker, las señales que tiene activas, el score y las señales True que tiene
    row_values = [screener.loc[ticker, 'Signals'], screener.loc[ticker, 'Score']] + list(signals.loc[ticker, signals.loc[ticker] == True].index.values)
    row_values += [None] * (len(screener_show.columns) - len(row_values))
    screener_show.loc[ticker] = row_values
    

#pasamos los DataFrames a un archivo csv y excel
#screener.to_csv('screener.csv')
#screener_show.to_csv('screener_show.csv')
screener.to_excel('screener.xlsx')
screener_show.to_excel('screener_show.xlsx')

