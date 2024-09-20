# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 10:58:36 2024

@author: USER
"""

import requests

def notify(msg, token):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + token}
    payload = {"message": msg,
               "stickerPackageId": 11538,
               "stickerId":51626494
               }


    requests.post(url, headers=headers, data=payload)


#token = "https://notify-bot.line.me/my/" #gernerall token from https://notify-bot.line.me/my/
#message = "今天天氣真好!!  "

#notify(message, token)
