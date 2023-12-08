FROM python:3.8

# set a directory for the app
WORKDIR /usr/src/app

# copy all the files to the container
COPY . .

# install dependencies

#python related dependencies
RUN pip install --upgrade pip
RUN pip install pathlib
RUN pip install selenium-wire
RUN pip install selenium
RUN pip install requests
RUN pip install undetected-chromedriver
RUN pip install filelock
RUN pip install psutil
RUN pip install pgrep

#chrome related dependencies
RUN apt-get update
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install ./google-chrome-stable_current_amd64.deb -y
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip
RUN apt-get install unzip -y
RUN unzip chromedriver-linux64.zip
RUN mv chromedriver-linux64/chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver