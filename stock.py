#import pandas as pd
import requests
import time
import json


# 打算要取得的股票代碼
stock_list_tse = ['0050', '0056', '2330', '2886']
stock_list_otc = [ '00679B']
    
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
print(data['msgArray'][0]['z'])
# 過濾出有用到的欄位
columns = ['c','n','z','tv','v','o','h','l','y', 'tlong']
df = pd.DataFrame(data['msgArray'], columns=columns)
df.columns = ['股票代號','公司簡稱','成交價','成交量','累積成交量','開盤價','最高價','最低價','昨收價', '資料更新時間']

# 自行新增漲跌百分比欄位
df.insert(9, "漲跌百分比", 0.0) 

# 用來計算漲跌百分比的函式
def count_per(x):
  try:
    x.iloc[0] = float( x.iloc[0])
    result = (x.iloc[0] - float(x.iloc[1])) / float(x.iloc[1]) * 100
  except ValueError:
    result = 0

  return pd.Series(['-' if x.iloc[0] == 0.0 else x.iloc[0], x.iloc[1], '-' if result == -100 else result])


# 填入每支股票的漲跌百分比
df[['成交價', '昨收價', '漲跌百分比']] = df[['成交價', '昨收價', '漲跌百分比']].apply(count_per, axis=1)

# 紀錄更新時間
def time2str(t):
  print(t)
  t = int(t) / 1000 + 8 * 60 * 60. # UTC時間加8小時為台灣時間
  
  return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))

# 把API回傳的秒數時間轉成容易閱讀的格式
df['資料更新時間'] = df['資料更新時間'].apply(time2str)

# 顯示股票資訊
#display(df)
print(df)
