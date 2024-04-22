import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import requests
import json
import os


max_mae = 6 # max mean square error that we allow our model to produce
n_observations = 48 

# N days to substract
days_substract = round(n_observations/24)

uri = os.environ.get("URI")
engine = create_engine(uri)


# get the largest predicted date
pred_resp = engine.execute("SELECT MAX(prediction_date) from predictions;")
largest_date = pred_resp.fetchall()

pred_initial_data = largest_date[0][0] - timedelta(days=days_substract)

# get all the predictions in said range
pred_data_resp = engine.execute(f"SELECT * FROM predictions WHERE prediction_date > '{pred_initial_data}';")
pred_data = pred_data_resp.fetchall()
colnames = pred_data_resp.keys()

# create DF from gathered predicted data
data = pd.DataFrame(pred_data, columns=colnames)
print(data.shape)
