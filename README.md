# sec-header-analysis

This script is being used to gather data on security headers in http requests as foundation for my bachelor thesis.

On execution it will access the top 1 million most visited sites according to [this site](https://tranco-list.eu/) through a headless browser and save the information of all http requests made during this process for further analysis.

# How to setup

Make sure to run this script on a linux system and have [docker](https://docs.docker.com/engine/install/) installed.

# How to start

```console
~$ ./start.sh
```

This will build the secheader docker image, if it doesn't exist already and/or run the image immediately.
