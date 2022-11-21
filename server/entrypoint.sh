#!/bin/bash

if [[ ! -z "$DB_HOST" && ! -z "$DB_PORT" ]]; then
  echo "Waiting for postgres ($DB_HOST:$DB_PORT)..."

  while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
  done
  sleep 1

  echo "PostgreSQL started"
  echo "applying migrations..."
  python manage.py migrate
  echo "migrations applied"

fi
exec "$@"