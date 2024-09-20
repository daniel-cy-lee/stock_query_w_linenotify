#import pandas as pd
import requests
import time
import json
from mypassword import MyPassword
from line_notify import notify

# 打算要取得的股票代碼
stock_list_tse = ['0050', '0056', '2330', '2317',  ]
stock_list_otc = ['00679B']
#stock_list_tse = ['0050']
#stock_list_otc = []

# 組合API需要的股票清單字串
stock_list1 = '|'.join('tse_{}.tw'.format(stock) for stock in stock_list_tse)

# 6字頭的股票參數不一樣
stock_list2 = '|'.join('otc_{}.tw'.format(stock) for stock in stock_list_otc)
stock_list = stock_list1 + '|' + stock_list2
print(stock_list)

#　組合完整的URL
query_url = f'http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={stock_list}'
print(query_url)

# 呼叫股票資訊API
response = requests.get(query_url)

# 判斷該API呼叫是否成功
if response.status_code != 200:
  raise Exception('取得股票資訊失敗.')
else:
  print(response.text)

# 將回傳的JSON格式資料轉成Python的dictionary

data = json.loads(response.text)

# 紀錄更新時間
def time2str(t):
  t = int(t) / 1000 #+ 8 * 60 * 60. # UTC時間加8小時為台灣時間

  return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))

# 過濾出有用到的欄位
def extra_data(data):
  text_str = "\n"
  for it in data['msgArray']:
    id = it['c']
    name = it['n'].strip()
    bid = float(it['z'])
    yestoday = float(it['y'])
    cratio = (bid -yestoday)/yestoday*100
    time_str = time2str(it['tlong'])
    text_str += ("股票代號: {:<6}\n公司簡稱: {:<20}\n成交價: {:<3.2f}\n漲跌百分比: {:<2.2f}\n資料更新時間 {}"
        .format(id, name, bid, cratio, time_str)) +"\n\n"
  return text_str

str_msg = extra_data(data)
print(str_msg)

token = MyPassword.line_token_stock
notify(str_msg, token)
