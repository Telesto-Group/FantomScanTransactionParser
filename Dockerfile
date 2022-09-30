FROM ubuntu:20.04

RUN apt-get update && apt-get install git python3-pip -y
RUN pip3 install requests
