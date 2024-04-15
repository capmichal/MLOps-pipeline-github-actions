# docker image recommended by FastAPI
FROM tiangolo/uvicorn-gunicorn:python3.10

# copy our api program to workdir
COPY api.py api.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "api:app", "--reload", "--port", "8000"]
