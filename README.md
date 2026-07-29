# CPHO server

See the CPHO slack channel's link bar for the dev app's URL  

## Setting up the development environment

Note: run all this in the repo's root directory

1. install python3.10 
2. install postgres [instructions here](https://github.com/PHACDataHub/phac-django-docs/blob/master/local-dev.md#installing-and-using-postgres-wout-sci-ops-on-windows) 
3. clone repo
4. create a virtual environment in repo root (python -m venv venv)
5. activate virtual environment (source venv/Scripts/activate on windows, venv/bin/activate on *nix)
6. install dependencies (`pip install -r server/requirements.txt -r server/requirements_dev.txt`)
7. (if applicable) Start the db server: `pg_ctl -D ~/pg/data/ -l logfile start`
8. setting postgres:

    ```
    ./server/dev-db-init.sh
    ```
    <!-- - ```bash
        psql -U postgres -c "CREATE ROLE cpho_db_user with login"
        psql -U postgres -c "ALTER ROLE cpho_db_user createdb"
        createdb -U cpho_db_user cpho_dev_db
        ``` -->
9. seed the DB
    - ```bash
        python ./manage.py migrate
        python ./manage.py loaddata cpho/fixtures/dimension_lookups.yaml
        python ./manage.py loaddata cpho/fixtures/periods.yaml
        python -m manage seed_countries --mode reset --yes
        python ./manage.py runscript cpho.scripts.dev
        ```
10. `python manage.py runserver`

### Other useful dev commands:

resetting dev db: 
```bash
dropdb -U cpho_db_user cpho_dev_db;
createdb -U cpho_db_user cpho_dev_db;
```

Resetting test db (useful when migrations get in the way of running tests)
```bash
dropdb -U cpho_db_user cpho_test_db
```


### Manually running format commands

In the case your CI is failing due to formatting issues, you can run the following commands to fix them all.

1. `isort server --settings-path pyproject.toml`
2. `black server/ --config pyproject.toml`
3. `djlint --reformat server --configuration pyproject.toml`



## Using SQlite

Note: if you set USE_SQLITE=True in your .env file, you don't need to set any of the DB-related environment variables and the app will use sqlite instead of postgres. This is useful for testing/development, especially on the PHAC workstations. Note that changelogs won't work with sqlite, so those tests will always fail.

## Remote DB manipulation

To connect to the remote DB from your local machine, download, chmod and ensure the cloud-sql-proxy is in your path, then run `source deploy/connect_cloud_sql_proxy.sh`. In a different shell, you can now run `./manage.py` commands directly against the remote DB. Be careful and make sure you close the script process when you're done.

### Generating test coverage

From the `server/` directory run the following
1. `coverage run --source=. ./manage.py test tests/`
2. `coverage html -i`
3. `python -m http.server 1337`
4. visit `http://localhost:1337/htmlcov/` and dig into modules to see which individual line coverage


## Selenium tests

There are a few tests that use a live browser to test interaction. These do not run by default. You'll have to run them via `python manage.py test --selenium tests/selenium/`. 

These tests should work both in postgres and sqlite. But when using postgres, if anything goes wrong, the DB may not reset correctly and you may have to reset it (see dropdb test db command above).

You can run regular tests or these tests, never both at the same time. Do not attempt to run regular tests with --selenium or selenium tests without it, or else it will error and you will need to reset the test DB. 
