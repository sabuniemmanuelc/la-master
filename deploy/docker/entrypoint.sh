#!/bin/sh

echo "Collecting static..."
poetry run python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating MR. ROBOT..."
python manage.py create_mr_robot

echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
