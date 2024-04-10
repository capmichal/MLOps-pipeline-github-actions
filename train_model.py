# import general libraries
import pandas as pd
import pickle

# import model training libraries
from skforecast.model_selection import grid_search_forecaster
from skforecast.ForecasterAutoregCustom import ForecasterAutoregCustom
from sklearn.ensemble import RandomForestRegressor
from skforecast.ForecasterAutoreg import ForecasterAutoreg

# imports for data reading
import requests
from datetime import datetime

# imports for Neptune
import os
from dotenv import load_dotenv
import neptune
load_dotenv()

# To get started with Neptune and obtain required credentials refer to this page: https://docs.neptune.ai/setup/installation/.
NEPTUNE_API_KEY = os.environ.get('NEPTUNE_API_KEY')
NEPTUNE_PROJECT = os.environ.get('NEPTUNE_PROJECT')
# Data
steps = 36
n_datos_entrenar = 200
path_fichero = 'bitcoin.csv'
path_modelo = 'model.pickle'
#uri_mlflow = 'http://104.198.136.57:8080/' no need to use currently ?
experiment_name = "bictoin_transactions"

# Extract info from Bitcoin
url = 'https://api.blockchain.info/charts/transactions-per-second?timespan=all&sampled=false&metadata=false&cors=true&format=json'
resp = requests.get(url)

data = pd.DataFrame(resp.json()['values'])

# Coerce dates
data['x'] = [datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') for x in data['x']]
data['x'] = pd.to_datetime(data['x'])

# renaming columns
data.columns = ['date', 'transactions'] # way better than df.rename(XXXXX)

# Get hourly data
data['date'] = data['date'].dt.round('H')
grouped_data = data.groupby('date').sum().reset_index()


# additional frequency settings missed from original neptune.ai code
grouped_data = grouped_data.set_index('date')
grouped_data = grouped_data.asfreq("H")

# Train test split
train_data = grouped_data[ -n_datos_entrenar:-steps]
test_data  = grouped_data[-steps:]

# Define forecaster
forecaster_rf = ForecasterAutoreg(
                    regressor      = RandomForestRegressor(random_state=123),
                    lags    = 20
                )

# Define grid search
param_grid = { 'n_estimators': [100, 500], 'max_depth': [3, 5, 10] }

grid_results = grid_search_forecaster(
                        forecaster  = forecaster_rf,
                        y           = train_data["transactions"],
                        param_grid  = param_grid,
                        steps       = 10,
                        metric      = 'mean_squared_error',
                        initial_train_size    = int(len(train_data)*0.5),
                        allow_incomplete_fold = True,
                        return_best = True, # return only ONE best grid
                        verbose     = False
                    )

# Upload metadata to Neptune
# we will make as many RUNS in neptune app as there are results (grid result models)
for i in range(grid_results.shape[0]):

  run = neptune.init_run(
      project= NEPTUNE_PROJECT,
      api_token=NEPTUNE_API_KEY,
  )

  params = grid_results['params'][i]
  run["parameters"] = params
  run["mean_squared_error"] = grid_results['mean_squared_error'][i]

  run.stop()

# Save model locally
last_training_date = test_data.index[-1].strftime('%Y-%m-%d %H:%M:%S')
pickle.dump(last_training_date, open('last_training_date.pickle', 'wb'))
pickle.dump(forecaster_rf, open(path_modelo, 'wb'))