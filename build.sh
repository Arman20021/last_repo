#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# This line loads your local data automatically during deployment
python manage.py loaddata local_data.json