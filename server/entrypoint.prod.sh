#!/bin/bash
echo "Starting SSH server..."
service ssh start

echo "Generating static files..."
python manage.py collectstatic --no-input

if [ ! -z "$DB_HOST" ] && [ ! -z "$DB_PORT" ]; then
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

eval $(printenv | sed -n "s/^\([^=]\+\)=\(.*\)$/export \1=\2/p" | sed 's/"/\\\"/g' | sed '/=/s//="/' | sed 's/$/"/' >> /etc/profile)

exec gosu ${APP_USER} "$@"
