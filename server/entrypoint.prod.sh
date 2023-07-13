#!/bin/sh
set -o errexit
set -o pipefail
set -o nounset

# WARNING: this needs to run inside the app docker container, which is alpine linux
# That means sh instead of bash, different unix utilities, etc

if [[ -f /secrets/.env.prod ]]; then
  echo "Found .env.prod in mounted secrets volume, copying to ${APP_HOME}"
  cp /secrets/.env.prod "${APP_HOME}"
fi

# I'd love for this to be a Docker build time step, but there's subtle differences to the
# output depending on if .env.dev or .env.prod is used, so it can't happen sooner than here
echo "Running collectstatic..."
python manage.py collectstatic --no-input

echo "Applying migrations..."
python manage.py migrate

# TODO: this is a workaround, to be replaced when working out a proper data migration approach, possibly
# temporary dev expedient, uncomment to seed the DB while deploying the app. Note: you also need to temporarily
# install requirements_dev.txt during the Docker file BUILDER layer for these to run
#python ./manage.py loaddata cpho/fixtures/dimension_lookups.yaml
#python ./manage.py loaddata cpho/fixtures/periods.yaml
#python ./manage.py runscript cpho.scripts.dev

# Execute the docker CMD (either the default in the Dockerfile or an over ride from the command line)
exec "$@"
 