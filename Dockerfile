FROM apache/airflow:2.6.2

USER root
RUN pip install pandas pyppeteer
# Install dependencies required for Google Chrome
RUN apt-get update && apt-get install -y wget libxss1 

# Download and install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN apt-get --fix-broken install
