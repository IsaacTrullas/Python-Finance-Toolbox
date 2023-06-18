import requests
import pandas as pd 
from yahoo_fin import stock_info as si
import numpy as np

tickers = si.tickers_sp500()
#tickers = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']
data = pd.DataFrame(columns =['Stock', 'recomendacion'])

for ticker in tickers:
    url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
    parametros = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
              'modules=upgradeDowngradeHistory,recommendationTrend,' \
              'financialData,earningsHistory,earningsTrend,industryTrend&' \
              'corsDomain=finance.yahoo.com'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


    url = url + ticker + parametros
    r = requests.get(url, headers=headers)
    
    result = r.json()['quoteSummary']['result'][0]
    recomendacion =result['financialData']['recommendationMean']['fmt']
    
    #añadimos una nueva fila a data con el ticker y la recomendacion usando concat
    data = pd.concat([data, pd.DataFrame([[ticker, recomendacion]], columns=['Stock', 'recomendacion'])], ignore_index=True)    
    
    ticker, recomendacion
    #time.sleep(0.5)
    
data.to_excel('recommendacion_stocks.xlsx')
#data.to_csv('recommendacion_stocks.csv')

data