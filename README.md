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

## #Other useful dev commands:

resetting dev db: 
```bash
dropdb -U cpho_db_user cpho_dev_db;
createdb -U cpho_db_user cpho_dev_db;
```

Resetting test db (useful when migrations get in the way of running tests)
```bash
dropdb -U cpho_db_user cpho_test_db
```


## Remote DB manipulation

To connect to the remote DB from your local machine, download, chmod and ensure the cloud-sql-proxy is in your path, then run `source deploy/connect_cloud_sql_proxy.sh`. In a different shell, you can now run `./manage.py` commands directly against the remote DB. Be careful and make sure you close the script process when you're done.
