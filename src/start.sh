#!/bin/bash

pkill Xvfb
xvfb-run --server-args="-screen 0 1900x1200x24" python /app/src/main.py