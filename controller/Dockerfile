FROM python:3.7-stretch

WORKDIR /usr/src/app

# RUN apt-get update && apt-get install -y build-essential unzip wget

# RUN wget http://abyz.co.uk/rpi/pigpio/pigpio.zip && unzip pigpio.zip && cd PIGPIO && make install
ENV test=3

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]