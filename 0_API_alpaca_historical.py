import requests
import pandas as pd
import datetime as dt
import time
import json

import _KEYS_DICT

# Alpaca endpoint URL
base_url = "https://data.alpaca.markets/v2/stocks/"

# Your Alpaca API key ID and secret
print("YOU MUST TO GET ALAPACA KEYS IN https://alpaca.markets/deprecated/docs/api-documentation/how-to/account/ ")
headers = {
    'APCA-API-KEY-ID': 'your alpaca key',
    'APCA-API-SECRET-KEY': 'your alpaca key',
}

def get_bars(symbol, start_date, end_date, timeframe='1Min', limit=10000):
    df_list = []  # List to hold batches of dataframes
    page_token = None  # Page token for pagination

    while True:
        # Request parameters
        params = {
            'timeframe': timeframe,
            'start': start_date,
            'end': end_date,
            'limit': limit,
            'page_token': page_token,  # Add page_token to parameters
            # "type": "market",
        }

        # Make the GET request
        response = requests.get(f"{base_url}{symbol}/bars", headers=headers, params=params)

        # Check the response
        if response.status_code != 200:
            print(f"Failed response URL {symbol}: {response.url}")
            print(f"Failed response to fetch data for {symbol}: {response.content}  ErrorCode: : {response.status_code} ")
            print(f"Dict response hearders keys {dict(response.headers) }")
            break

        data = response.json()

        if not data['bars']:
            print(f"No data found for {symbol} in the given date range.")
            break

        # Create a DataFrame and only keep 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'
        df = pd.DataFrame(data['bars'])
        df = df[['t', 'o', 'h', 'l', 'c', 'v']]

        # Rename the columns as per your requirement
        df.rename(columns={'t':'Date', 'o':'Open', 'h':'High', 'l':'Low', 'c':'Close', 'v':'Volume'}, inplace=True)

        # Convert the 'Date' column to datetime format and set it as index
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        # Append the DataFrame to the list
        df_list.append(df)

        # If a next page token is present, continue fetching data, else break
        if 'next_page_token' in data and data['next_page_token'] is not None:
            # print(f"Fetching next page with token {data['next_page_token']}")
            page_token = data['next_page_token']
        else:
            print("No more pages to fetch.")
            break

    # Concatenate all the dataframes in the list
    final_df = pd.concat(df_list)

    # Return the final DataFrame
    return final_df



# Set your parameters
# symbol = 'AAPL'  # Replace with the symbol you're interested in
START_DATE = '2019-01-01T00:00:00Z'
END_DATE = '2023-07-10T23:59:59Z'
CSV_NAME = "@CHILL"
stocks_list = _KEYS_DICT.DICT_COMPANYS[CSV_NAME]


for symbol in stocks_list:
    # Fetch the data
    print("Starting data fetching process Stock: ", symbol)
    df = get_bars(symbol, START_DATE, END_DATE)
    print("Data fetching process completed df.shape: ", df.shape)

    # Save the data as a CSV file
    if df is not None:
        df.index = pd.to_datetime(df.index)#Get TypeError: Index must be DatetimeIndex
        TIME_ALPHA_OPEN = "13:30:00";TIME_ALPHA_CLOSE = "20:00:00";
        df = df.between_time(TIME_ALPHA_OPEN, TIME_ALPHA_CLOSE)
        # df.to_csv(f"data/alpa_{symbol}_1min.csv",sep="\t")
        # print(f"Data saved as ", f"data/alpa_{symbol}_1min.csv")
        max_recent_date = df['Date'].max()[:10].replace('-', '')  # pd.to_datetime().strftime("%Y%m%d")
        min_recent_date = df['Date'].min()[:10].replace('-', '')  # pd.to_datetime( ).strftime("%Y%m%d")
        print("d_price/RAW_alpha/alpha_" + symbol + '_' + '1Min' + "_" + max_recent_date + "__" + min_recent_date + ".csv")
        df.to_csv("d_price/RAW_alpha/alpha_" + symbol + '_' + '1Min' + "_" + max_recent_date + "__" + min_recent_date + ".csv",sep="\t", index=None)
        print("\tSTART: ", str(df.index.min()),  "  END: ", str(df.index.max()) , " shape: ", df.shape, "\n")
    else:
        print ("error none in stock: ", symbol)

