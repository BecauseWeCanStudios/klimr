#!/bin/bash
#. ../../venv/bin/activate;
uwsgi --ini uwsgi.conf;
#sg www-data 'uwsgi --ini uwsgi.conf';

