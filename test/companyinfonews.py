#### 
# Author: Aycan Katitas 
# Description: Recent Sustainability News
# Date: 10/11/2023
####

import requests
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv 


load_dotenv()

AV_API_KEY = "8X52OCUIN0Z13TRG"

symbol = "BP"
url = "https://www.alphavantage.co/query"

## Company Info 

params = {
    "function": "OVERVIEW",
    "symbol": symbol, 
    "apikey": AV_API_KEY
}


response = requests.get(url,params=params)
data = response.json()
def company_overview(symbol):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": AV_API_KEY
    }

    # Send a GET request to the API
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if not data:
            print(f"No data found for {symbol}")
            return None
        extracted_data = {
            "Symbol": data.get("Symbol"),
            "AssetType": data.get("AssetType"),
            "Name": data.get("Name"),
            "Description": data.get("Description"),
            "CIK": data.get("CIK"),
            "Exchange": data.get("Exchange"),
            "Currency": data.get("Currency"),
            "Country": data.get("Country"),
            "Sector": data.get("Sector"),
            "Industry": data.get("Industry"),
            "Address": data.get("Address"),
            "FiscalYearEnd": data.get("FiscalYearEnd"),
            "LatestQuarter": data.get("LatestQuarter"),
            "MarketCapitalization": safe_float(data.get("MarketCapitalization")),
        }
        
    else:
        print(f"Error: {response.status_code} - {response.text}")

    return extracted_data





## News Sentiment 
params = {
    "function": "NEWS_SENTIMENT",
    "tickers": symbol,
    "apikey": AV_API_KEY,
    "sort": "RELEVANCE",
    "limit":1000,
    "time_from":"20230901T0100"
}
# Send a GET request to the API
response = requests.get(url, params=params)

data = response.json()

res_num = data["items"]

data["feed"][5]

print(f"Search found {res_num} articles for company {symbol}")



    if response.status_code == 200:
        data = response.json()
        if not data:
            print(f"No data found for {symbol}")
            print(data)
            return None
        news = []


