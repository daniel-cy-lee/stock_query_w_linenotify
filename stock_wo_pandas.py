import requests
import time
import json
import traceback
import logging
from dataclasses import dataclass

#
def time2str(t):
  t = int(t) / 1000 #+ 8 * 60 * 60. # UTC時間加8小時為台灣時間

  return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
def a2f(str_value, default = 0):
    try:
      value = float(str_value)
    except ValueError as e:
      print(e)
      print(traceback.format_exc())
      logging.warning(traceback.format_exc())
      value = default
    return value

'''
  五檔報價的委買價與委賣價
  在五檔報價中，“委買價”位於報價表的左側，依序顯示從高到低的五個買入價格。而“委賣價”位於右側，顯示從低到高的五個賣出價格。這些報價並不代表已成交的價格，而是市場中目前的掛單狀況。下單時，內外盤的數據會影響買賣價位的變化。

'''
def split_ask(ask_list):
   values = ask_list.split('_')
   values = values[:-1] #delete last item in list
   return values


def query():
  logging.basicConfig(level=logging.INFO, filename='log.txt', filemode='a',
  	format='[%(asctime)s %(levelname)-8s] %(message)s',
  	datefmt='%Y%m%d %H:%M:%S',
  	)
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
  logging.info(data)




  '''
  (*1) bid  成交價
  買方要價與賣方要價不等於成交價
  逐筆撮合，若查詢當下沒有成交買賣，也就沒殺成交價

  當 JSON 資料中沒有顯示成交價（也就是「最新成交價」），你可以根據以下幾種方式來處理：

  查詢前一筆成交價
  如果沒有最新的成交價，你可以使用前一次的成交價（如果有的話）。在這個 JSON 中，"z" 欄位通常會記錄最後成交價。這裡的值是 "z": "183.1000"，所以你可以視為這是最後成交價。

  判斷市場是否尚未有成交
  如果當前時間內未發生任何成交，成交價可能顯示為 - 或 null。這種情況下，價格只能由買賣雙方掛出的買入價（b 欄位）和賣出價（a 欄位）來參考，等待成交。

  使用開盤價或收盤價
  在某些情況下，如果沒有最新的成交價，通常可以使用開盤價（o 欄位）來暫代。此外，若是盤後情境，可以使用前一交易日的收盤價（y 欄位）來作為參考。

  ==> 目前作法: 使用買方出價最一筆(最低出價)代替
  '''
  # 過濾出有用到的欄位
  @dataclass
  class Stock:
    stock_id: str
    name: str
    open: float
    high: float
    low: float
    ask_list: list()
    buy_list: list()
    bid: float
    yeastoday: float
    cratio: float
    time_int: int
  def extra_data(data):
    stock = []
    for it in data['msgArray']:
      id = it['c']
      name = it['n'].strip()
      open = a2f(it['o'], 0)
      high = a2f(it['h'], 0)
      low = a2f(it['l'], 0)
      ask_list = split_ask(it['a'])
      buy_list = split_ask(it['b'])
      bid = a2f(it['z'], a2f(buy_list[-1], 0)) #成交價(或出價)(*1)
      yestoday = a2f(it['y'], 0)
      cratio = (bid - yestoday)/yestoday*100
      time_int = it['tlong']
      next = Stock(id, name, open, high, low, ask_list, buy_list, bid
             ,yestoday, cratio, time_int)
      stock.append(next)

    return stock

  stock = extra_data(data)
  return stock

'''
# using sample
stock = query()
print(stock)
'''

def stock_2_line():
  from mypassword import MyPassword
  from line_notify import notify
  stock = query()

  msg_str = "\n"
  for it in stock:
    time_str = time2str(it.time_int)
    msg_str += ("{}({:<6})\n成交價: {:<3.2f}\n漲跌百分比: {:<2.2f}\n委買價: {:.2f}-{:.2f}\n委賣價: {:.2f}-{:.2f}\n最高價: {:<3.2f}\n最低價: {:<3.2f}\n開盤價: {:<3.2f}\n資料更新時間 {}"
        .format(it.name, it.stock_id, it.bid, it.cratio, a2f(it.buy_list[0]), a2f(it.buy_list[-1]),
                a2f(it.ask_list[0]), a2f(it.ask_list[-1]), it.high, it.low, it.open, time_str)) +"\n\n"

  token = MyPassword.line_token_stock
  notify(msg_str, token)
  #notify(msgi_str, MyPassword.line_token_p2p)
