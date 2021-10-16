# HTTP Service
## 

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)


## Problem Statement

> Our customers are sending billions of requests each day that need to be processed. Today, all incoming requests are processed regardless of their validity, leading to slower processing. We want to filter out invalid requests (badly formatted, containing invalid values, missing required fields, …) but keep a history on a day-by-day basis so that we can properly charge customers for the traffic they send.

## Installation
### Using Code
> This service requires [Python](https://www.python.org/) v3.7+ to run.

Install pipenv to install the dependencies and devDependencies

```pip install pipenv
pipenv install
```
To active the pipenv virtual environment
```
pipenv shell
```

To start the application
```
uvicorn api:app
```
### Using Docker
By default, the Docker will expose port 8000, so change this within the Dockerfile if necessary. When ready, simply use the Dockerfile to build the image.

```sh
cd <directory-containing-dockerfile>
docker build -t <buildImageTag> .
```

This will create the serivce image and pull in the necessary dependencies.

Once done, run the Docker image and map the port to whatever you wish on your host. In this example, we simply map port 8080 of the host to port 8000 of the Docker (or whatever port was exposed in the Dockerfile):

```sh
docker run -p 8080:8000 <buildImageTag>
```

>
Verify the deployment by navigating to your server address in your preferred browser.

```sh
127.0.0.1:8000/docs
```


## Testing and Usage

The api can be tested via Postman or any API platform. Also for further documentation for usage please visit the http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc after running the application
> Note: `127.0.0.1:8000` is the deafult configuration, please replace the IP and port with your appropriate IP and port





