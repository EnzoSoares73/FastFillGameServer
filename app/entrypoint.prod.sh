#!/bin/bash

echo "Subindo aplicação"
python -m gunicorn fastfillgame.wsgi:application --bind 0.0.0.0:8000
