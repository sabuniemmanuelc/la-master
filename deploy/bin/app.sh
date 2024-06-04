#!/bin/sh
PATH="/home/pollycode/.local/bin:$PATH"
poetry install
poetry run python manage.py collectstatic --noinput
poetry run python manage.py migrate --noinput
poetry run python manage.py create_mr_robot
# poetry run celery -A la worker --loglevel=warning
poetry run gunicorn --workers 21 --bind unix:/opt/la/run/la.sock la.wsgi:application \
--error-logfile /opt/la/logs/gunicorn_error.log --access-logfile /opt/la/logs/gunicorn_access.log \
--capture-output --log-level debug --reload
