# CPHO server



## Example .env file: 

```
TEST_DB_NAME=cpho_test_db
DB_NAME=cpho_dev_db
DB_USER=cpho_db_user
DB_PASSWORD=""
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=abcdefg

# dev settings
ALLOWED_HOSTS=*
DEBUG=True
IS_LOCAL_DEV=True

# required for debug toolbar
ENABLE_DEBUG_TOOLBAR=True
INTERNAL_IPS=127.0.0.1

# this is to disable session timeout
PHAC_ASPC_SESSION_COOKIE_AGE=99999999 # this doesn't seem to work?
PHAC_ASPC_SESSION_COOKIE_SECURE=0
EOF
```

# Setting up the development environment

Note: run all this in the repo's root directory

1. install python3.10 
2. install postgres [instructions here](https://github.com/PHACDataHub/phac-django-docs/blob/master/local-dev.md#installing-and-using-postgres-wout-sci-ops-on-windows) 
3. clone repo
4. create a virtual environment in repo root (python -m venv venv)
5. activate virtual environment (source venv/Scripts/activate on windows, venv/bin/activate on *nix)
6. install dependencies (`pip install -r server/requirements.txt -r server/requirements_dev.txt`)
7. setting postgres:
    - ```bash
        psql -U postgres -c "CREATE ROLE cpho_db_user with login"
        psql -U postgres -c "ALTER ROLE cpho_db_user createdb"
        createdb -U cpho_db_user cpho_dev_db
        ```
8. seed the DB
    - ```bash
        python ./manage.py migrate
        python ./manage.py loaddata cpho/fixtures/dimension_lookups.yaml
        python ./manage.py loaddata cpho/fixtures/periods.yaml
        python ./manage.py runscript cpho.scripts.dev
        ```
9. `python manage.py runserver`

## Other useful commands:

resetting dev db: 
```bash
dropdb -U cpho_db_user cpho_dev_db;
createdb -U cpho_db_user cpho_dev_db;
```

Resetting test db (useful when migrations get in the way of running tests)
```bash
dropdb -U cpho_db_user cpho_test_db
```

