import pandas as pd
import requests
from datetime import datetime
from sqlalchemy import create_engine
import os

uri = os.environ.get('URI') # from secrets


url = 'https://api.blockchain.info/charts/transactions-per-second?timespan=all&sampled=false&metadata=false&cors=true&format=json'

resp = requests.get(url)
data = pd.DataFrame(resp.json()["values"])

# from timestamp to date
data['x'] = [datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') for x in data['x']]
data['x'] = pd.to_datetime(data['x'])


# Currently we do not handle NON EXISTING TABLE error, so our database MUST have such tables
engine = create_engine(uri)
query = engine.execute('SELECT MAX(reality_date) FROM reality;')
last_reality_date = query.fetchall()[0][0]
query.close()


# last prediction from database, again no error handling
engine = create_engine(uri)
query = engine.execute('SELECT MIN(prediction_date), MAX(prediction_date) FROM predictions;')
prediction_date= query.fetchall()[0]
query.close()

# find out since when do we have to gather data
first_prediction_date = prediction_date[0]
last_prediction_date = prediction_date[1]

if last_reality_date is None:
    date_extract = first_prediction_date

elif  last_reality_date <= last_prediction_date:
    date_extract = last_reality_date

else:
    date_extract = last_reality_date


# rounding hours to get hourly data
data['x'] = data['x'].dt.round('H')

# getting the number of transactions per hour
data_grouped = data.groupby('x').sum().reset_index()

# getting the data from the last data available in the database
data_grouped = data_grouped.loc[data_grouped['x'] >= date_extract,:]


upload_data = list(zip(data_grouped['x'], round(data_grouped['y'],4)))
upload_data[:3]



# inserting the data in the database
for upload_day in upload_data:
    timestamp, reality= upload_day
    # ON CONFLICT error handling if case of any lag etc. resulting in already existing timestamp inside table
    result = engine.execute(f"INSERT INTO reality(reality_date, reality) VALUES('{timestamp}', '{reality}') ON CONFLICT (reality_date) DO UPDATE SET reality_date = '{timestamp}', reality= '{reality}';")
    result.close()

