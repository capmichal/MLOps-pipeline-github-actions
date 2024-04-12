from fastapi import FastAPI
app = FastAPI()
@app.post("/forecast")
def forecast(num_predictions = 168, return_predictions = True):

    import pandas as pd
    import requests
    from datetime import datetime
    from sqlalchemy import create_engine
    import pickle
    import os
    uri = os.environ.get('URI')

    # Load Files
    forecaster_rf = pickle.load(open('model.pickle', 'rb'))
    last_training_date = pickle.load(open('last_training_date.pickle', 'rb'))
    last_training_date = datetime.strptime(last_training_date, '%Y-%m-%d %H:%M:%S')

    # I obtain the data 
    url = 'https://api.blockchain.info/charts/transactions-per-second?timespan=all&sampled=false&metadata=false&cors=true&format=json'
    resp = requests.get(url)
    data = pd.DataFrame(resp.json()['values'])

    # I correct the date
    data['x'] = [datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') for x in data['x']]
    data['x'] = pd.to_datetime(data['x'])

    # I read the last prediction
    engine = create_engine(uri)
    query = engine.execute('SELECT MAX(prediction_date) FROM predictions;')
    last_prediction_date= query.fetchall()[0][0]
    query.close()

    # If there is no last date in the databse or training > database, I read the last date from training
    if  (last_prediction_date is None) or (last_prediction_date < last_training_date):

        # As there is no predictions, I make the predictions
        predictions = forecaster_rf.predict(num_predictions)

        fechas = pd.date_range(
            start = last_training_date.strftime('%Y-%m-%d %H:%M:%S'),
            periods = num_predictions,
            freq = '1H'
            )

    # sytuacje gdzie już używaliśmy naszego wytrenowanego modelu to stworzenia jakiejś predykcji
    elif last_prediction_date > last_training_date:
        # In this case, we must take into account the differences between the last forecast date and add the difference to the number of days to extract.
        dif_seg= last_prediction_date - last_training_date
        hours_extract = num_predictions + dif_seg.seconds//3600

        # we should make use of hours_extract now, to give MORE predictions than we already have
        # NIE MAMY odświeżonego modelu, przetrenowanego na nowych danych, ale musimy dać nowe predykcje
        # więc po prostu dajemy WIĘCEJ predykcji, dalej wybiegamy w przyszłosć
        predictions = forecaster_rf.predict(num_predictions)
        # I get the last predictions
        predictions = predictions[-num_predictions:]

        fechas = pd.date_range(
            start = last_prediction_date.strftime('%Y-%m-%d %H:%M:%S'),
            periods = num_predictions,
            freq = '1H'
            )
    else:
        # If last training > last predictions
        predictions = forecaster_rf.predict(num_predictions)

        fechas = pd.date_range(
            start = last_training_date.strftime('%Y-%m-%d %H:%M:%S'),
            periods = num_predictions,
            freq = '1H'
            )

    upload_data = list(zip([
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * num_predictions,
    [fecha.strftime('%Y-%m-%d %H:%M:%S') for fecha in fechas ],
        predictions
    ))

    # I insert the data
    for upload_day in upload_data:
        timestamp, fecha_pred, pred = upload_day
        pred = round(pred, 4)

        result = engine.execute(f"INSERT INTO predictions (timestamp, prediction_date,  prediccion) \
            VALUES('{timestamp}', '{fecha_pred}', '{pred}') \
            ON CONFLICT (prediction_date) DO UPDATE \
            SET timestamp = '{timestamp}', \
                prediccion = '{pred}' \
            ;")
        result.close()
    if return_predictions:
        predictions
    else:
        return 'New data inserted'