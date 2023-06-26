FROM apache/airflow:2.6.2

USER root
# Install dependencies required for Google Chrome
RUN apt-get update && apt-get install -y wget libxss1 

# Download and install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && apt-get --fix-broken install

RUN apt-get update \
    && apt-get install -y git

WORKDIR /home/airflow

RUN git clone https://github.com/VDV80/dvol_etl.git

# Change to the cloned repository directory
WORKDIR /home/airflow/dvol_etl

# to bring in dependancies mostly
RUN python setup.py install

RUN mkdir -p /home/airflow/Downloads

# Copy files with historical data already fetched to /home/airflow/Downloads
COPY ./mgp/* /home/airflow/Downloads