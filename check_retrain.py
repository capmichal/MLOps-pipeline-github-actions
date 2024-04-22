import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import requests
import json
import os
from sklearn.metrics import mean_absolute_error


max_mae = 6 # max mean absolute error that we allow our model to produce
n_observations = 48 

# N days to substract
days_substract = round(n_observations/24)

uri = os.environ.get("URI")
engine = create_engine(uri)

def get_data_for_mae(predictions=True):
    
    x = "prediction_date" if predictions else "reality_date"
    y = "predictions" if predictions else "reality"

    # get the largest predicted date
    pred_resp = engine.execute("SELECT MAX(prediction_date) from predictions;")
    largest_date = pred_resp.fetchall()

    pred_initial_data = largest_date[0][0] - timedelta(days=days_substract)

    # get all the predictions/realities in said range
    pred_data_resp = engine.execute(f"SELECT * FROM {y} WHERE ({x} > '{pred_initial_data}' and {x} <= '{largest_date[0][0]}');")
    pred_data = pred_data_resp.fetchall()
    colnames = pred_data_resp.keys()

    # create DF from gathered predicted data
    data = pd.DataFrame(pred_data, columns=colnames)
    return data

data = get_data_for_mae(predictions=True)
rel_data = get_data_for_mae(predictions=False)

actual_data = list(rel_data.reality)
predictions_data = list(data.prediction)

mae = mean_absolute_error(actual_data, predictions_data)

if mae > max_mae:
    # call github actions to retrain the model
    pass
