#!/bin/bash
source /home/me/bots/erjan/env/bin/activate
exec gunicorn -c "/home/me/bots/erjan/gunicorn_config.py" wsgi
