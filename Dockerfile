# docker image recommended by FastAPI
FROM tiangolo/uvicorn-gunicorn:python3.10

ARG URI
ENV URI $URI

# copy our api program to workdir
COPY api.py requirements.txt model.pickle last_training_date.pickle ./

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
