Not many models in production = cost of learning and using MLOps tools > benefits it returns
In such case there is no need to learn and include new concepts, we can build simple (but effective) MLOps pipelines
with one of the most used tools in software development: Github.


**How to create MLOps pipeline using Github Actions and a Cloud service provider.**
- data extraction pipeline : we need to create an ETL process that extracts the data, transforms it, and loads it somewhere (data lake, data warehouse or database)


When NOT to use this:
- many models you must put into production, or a few but **complex** models. Github actions machines do not provide enough computing power to train your models






NEPTUNE AI ARTICLE FIXES
- zdezaktualizowal sie sposob trenowania - zmieniona zew. biblioteka
- if statements wrong <> side
- not using hours_extract variable properly


REQUIREMENT EXTERNAL
sudo apt-get install libpq-dev

how to properly build this Dockerfile:
``` docker build . -t mlops_app:v0.1 --build-arg URI=$URI ```


#### GCP APPROACH TO CONTINUOUS DEPLOYMENT PIPELINE WITH CLOUD AND GITHUB
- each github push will put new docker image (API) to docker registry Google Cloud Build (AWS ECR)
- Google Cloud Run will deploy contenerized API to a service that scales down to 0 automatically, assiging required number of virtual machines (GCP Cloud Run can scale to 0 virtual machines running, which is something that AWS AppRunner cannot do)
