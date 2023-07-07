# WARNING: this needs to run inside the app docker container, which is alpine linux
# That means sh instead of bash, different unix utilities, etc

#!/bin/sh

if [[ -f "./.env.prod" ]]; then
  source "./.env.prod"
else
  source "./.env.dev"
fi


echo "applying migrations..."
python manage.py migrate

# temporary dev expedient, seed dev data (comment out after first run)
# to run these, you also need to uncomment the lines in the Dockerfile build step, to install requirements_dev.txt
# python ./manage.py loaddata cpho/fixtures/dimension_lookups.yaml
# python ./manage.py loaddata cpho/fixtures/periods.yaml
# python ./manage.py runscript cpho.scripts.dev

# Execute the docker CMD (either the default in the Dockerfile or an over ride from the command line)
exec "$@"
 