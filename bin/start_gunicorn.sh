#!/bin/bash
source /home/me/erjan/env/bin/activate
exec gunicorn -c "/home/me/erjan/gunicorn_config.py" wsgi
