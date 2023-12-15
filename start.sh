#!/bin/bash

/etc/init.d/mysql start
cd db_init
python3 init_populate.py
cd ../app
gunicorn -c ../configs/gunicorn_config.py --worker-class eventlet --workers 1 --bind 0.0.0.0:5000 app:app 2> /dev/null
