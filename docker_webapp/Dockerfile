FROM python:3.6

# Add code
ADD app/ /srv/klimr

# Install application requirements
ADD ./config/requirements.txt /srv/klimr/
RUN pip3 install -r /srv/klimr/requirements.txt

# Add start script
ADD ./config/start.sh /

# Add uWSGI config
ADD ./config/django-uwsgi.ini /etc/uwsgi/django-uwsgi.ini

# Add database check script
ADD ./config/database-check.py /srv/config/database-check.py

# Create django user, will own the Django app
RUN adduser --no-create-home --disabled-login --group --system django
RUN chown -R django:django /srv/klimr

# Execute start script
CMD ["./start.sh"]
