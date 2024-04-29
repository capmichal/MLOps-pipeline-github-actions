### How to Build MLOps Pipelines with GitHub Actions

#### PROS AND CONS of using Github Actions as MLOPs workflows

Not many models in production = cost of learning and using MLOps tools > benefits it returns
In such case there is no need to learn and include new concepts, we can build simple (but effective) MLOps pipelines
with one of the most used tools in software development: Github.

When NOT to use this:
- many models you must put into production, or a few but **complex** models. Github actions machines do not provide enough computing power to train your models

#### Pipeline explained step by step
- Setup data extraction pipeline with GitHub Actions - the number of bitcoin transactions per hour. 
- Build model-train and selection pipeline with GitHub Actions - for model evaluation / artifacts storage we could use Neptune.ai.
- Wrap the model as an API - FastAPI will allow us to use model as external API that will put predicted data in database hosted on AWS RDS.
- Dockerize the API for portability and easy use in production environment.
- Set up a continuous deployment pipeline with Cloud and GitHub Actions - each push to master branch will build a Docker image using best performing ML model and deploy it to AWS ECR.
- Automate model retrain with GitHub Actions - setup a Github actions workflow that will automatically evaluate model performance (predictions vs reality) and retrain/keep the model.


##### Properly building Dockerfile to handle env variables
how to properly build this Dockerfile:
``` docker build . -t mlops_app:v0.1 --build-arg URI=$URI ```

##### Setup requirements
- Database storing our predictions and reality to compare (AWS RDS was used in my project)
- NeptuneAI account to store information about all models
- Cloud Provider account to setup CI/CD with dockerized api


##### Installation
- ``` python3 -m venv venv ```
- ``` source venv/bin/activate ```
- ``` pip install -r requirements.txt ```


