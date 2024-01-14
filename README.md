# sec-header-analysis

This tool is being used to gather data on **security headers** in http requests as foundation for my **bachelor thesis**.

On execution it will crawl the top 1 million most visited sites according to the [Tranco list](https://tranco-list.eu/) through a headless browser and save the header information of all HTTP requests made during this process for further analysis.

# How to setup

Make sure to have **[docker](https://docs.docker.com/engine/install/)** and **[docker compose](https://docs.docker.com/compose/)** installed.

Configure website and process amount in the /src/config.py file.

# How to start

This will build the **secheader** docker image, if it doesn't exist already and run the image immediately:
```console
~$ docker compose up
```
