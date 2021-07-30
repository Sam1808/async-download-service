FROM ubuntu:20.04
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN apt-get update
RUN apt-get install -y zip
RUN apt-get install -y python3.8
RUN apt-get install -y python3-pip
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

