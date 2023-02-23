import requests
from datetime import datetime
from time import mktime
import pandas as pd

def _get_crumbs_and_cookies(stock):
    
    url = 'https://finance.yahoo.com/quote/{}/history'.format(stock)
    with requests.session() as s:
        headers = {
            'Connection': 'keep-alive',
            'Expires': '-1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        }
        s.headers.update(headers)
        
        website = s.get(url)
        return headers, website.cookies


def convert_to_unix(date):
    datum = datetime.strptime(date, '%d-%m-%Y')
    return int(mktime(datum.timetuple()))


def load_csv_data(stock, day_begin='30-10-1996', day_end='23-02-2023'):
    day_begin_unix = convert_to_unix(day_begin)
    day_end_unix = convert_to_unix(day_end)
    
    headers, cookies = _get_crumbs_and_cookies(stock)
    
    with requests.session() as s:
        headers.update({'Cookie': '; '.join([str(x) + '=' + str(y) for x, y in cookies.items()])})
        url = 'https://query1.finance.yahoo.com/v7/finance/download/{stock}?period1={day_begin}&period2={day_end}&events=history&includeAdjustedClose=true'.format(
            stock=stock, day_begin=day_begin_unix, day_end=day_end_unix)
        website = s.get(url, headers=headers)
        
        data = website.content.decode()
        lines = data.split('\n')
        result = []
        for line in lines:
            if line:
                result.append(line.split(','))
        
        data = pd.DataFrame(result[1:], columns=result[0])
        data['Date'] = pd.to_datetime(data['Date'])
        data.to_csv("benzdata.csv")
        return data

stock = "MBG.DE"
print(load_csv_data(stock))