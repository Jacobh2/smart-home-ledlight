# Ledstripe

Python service to control lights, for example LED stripes

## PiGPIO
Using the PiGPIO lib to control N-channel MOSFETs, with inspiration from [David Ordnung](https://dordnung.de/raspberrypi-ledstrip)


## Google Action Integration

The repo has built in support for Google Actions (used by the Google Home).

Requirements:

- service account key placed in `controller` folder called `smart-home-key.json`
- OAuth server; this repo comes with [Auth0](https://auth0.com/) support
    - To use, set the `AUTH_DOMAIN` and `API_AUDIENCE` envs

## Docker support

This repo comes with 2 sets of docker-compose files. One for x86 and one for ARM.

> Prebuilt arm images can be found [here](https://hub.docker.com/r/jacobh2/ledlight)

- Docker.arm
    - ARMv6 & ARMv7 support
- Docker
    - AMD64/x86 support

## Run docker

1. `docker run --rm -it --network=host --privileged lights`
2. exec into the container and run `pigpiod`

## Run docker compose with nginx

1. `docker-compose up --build -d`
2. First time, `exec` into container and run pigpiod

_In order to use SSL, make sure to put the `key.pem` and `cert.pem` files into the `webserver` folder_