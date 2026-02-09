#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create the superuser automatically using the env vars above
# We use || true so the build doesn't fail if the user already exists
python manage.py createsuperuser --noinput || true