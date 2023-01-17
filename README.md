# Pipline for scraping "https://apa.az/az" website
First all news that belongs to "2023" will be scraped. Then after each hour only new news will be added to the database.
The uniqueness of urls is ensured by adding CONSTRAINT to the "url" column of the table while creating table.
## Docker
#### Creating network for containers to communicate.
```docker
docker network create myNetwork
```
#### PostgreSQL database

Downloading PostgreSQL image
```docker
docker pull postgres 
```
Running PostgreSQL container from the postgres image in "myNetwork" network with below credentials.
```docker
docker run --name postgres-cnt-0 -e POSTGRES_USER=nurlan -e POSTGRES_PASSWORD=1234  --network="myNetwork" -d postgres
```
Creating "neurotime" database inside the "postgres-cnt-0" container.
```docker
docker exec -it postgres-cnt-0 bash
# psql -U nurlan
# create database neurotime;
```

#### Application dockerization
Building an image of the application
```docker
docker image build -t apa_az:1.0 .
```
Running a container from the image in "myNetwork" network.
```docker
docker run  --name apa_az_cnt --network="myNetwork" -d  apa_az:1.0
```
