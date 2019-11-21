# Ledstripe

Python service to control LED stripe

Inspiration from https://dordnung.de/raspberrypi-ledstrip

`+` Google Action integration

## Build docker image

`docker build -t lights -f Docker.arm controller`

## Run docker

1. `sudo pigpiod`
2. `docker run --rm -it --network=host --privileged lights`

## Run docker compose with nginx

1. `docker-compose up --build -d`
2. First time, `exec` into container and run pigpiod

_In order to use SSL, make sure to put the key and cert into the webserver folder_