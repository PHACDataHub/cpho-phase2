# CPHO Phase 2

[![Docker Image CI](https://github.com/PHACDataHub/cpho-phase2/actions/workflows/docker-image.yml/badge.svg)](https://github.com/PHACDataHub/cpho-phase2/actions/workflows/docker-image.yml)

### Note: This is _very much_ a work in progress. Work needs to be done to transform this prototype into an usable production application.

# How to run locally

# Docker

1. Install [Docker](https://docs.docker.com/install/) and have it running

2. Create a `.env` file in the root of the project with the following contents, and replace the fields as needed

   To generate a secret key, you can use tools such as [RandomKeygen](https://randomkeygen.com) to generate a strong key

   Feel free to modify the database and pgadmin credentials

   ```
   DEBUG=True

   ALLOWED_HOSTS=localhost,127.0.0.1

   # DATABASE SETTINGS
   DB_NAME=cpho_dev
   DB_USER=cpho_user
   DB_PASSWORD=123
   DB_HOST=pg
   DB_PORT=5432
   SECRET_KEY= # ADD GENERATED KEY HERE #

   # PGADMIN CONTAINER
   PGADMIN_DEFAULT_EMAIL=admin@example.com
   PGADMIN_DEFAULT_PASSWORD=123
   PGADMIN_LISTEN_PORT=5433
   PGADMIN_CONFIG_SERVER_MODE=False
   PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED=False
   PGADMIN_CONFIG_UPGRADE_CHECK_ENABLED=False
   ```

3. Run `docker compose up -d` in the root directory of the project

4. Docker should have created 4 containers:
   - `pg_container`: PostgreSQL database
   - `cpho_server_container`: Django Server
   - `pgadmin_container`: PGAdmin Server
   - `cpho_frontend_container`: React Frontend

Now, you can do the following:

- Navigate to `localhost:3000` to view the frontend

- Navigate to `localhost:8000/graphql` to view the GraphQL interface

- and `localhost:5433` to view the PGAdmin interface (note that this may take a few minutes to load, you can check the Docker container logs to see its progress)

When you're done working, you can run `docker compose down` to stop the containers

## Known issue with Windows

If you run into `exec /server/entrypoint.sh: no such file or directory` while starting the server container, please do the following:
<br/><img src="https://user-images.githubusercontent.com/50898635/203863894-190861e9-9d18-4d97-8d32-4ff653d7eb70.png" width="500"/>
[source](https://stackoverflow.com/questions/40452508/docker-error-on-an-entrypoint-script-no-such-file-or-directory)

# Without Docker

Assumes you have Python installed in system (check using `python --version` or `py --version`).

## Backend

1. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

   If the command above does not work, try:

   ```bash
   py -m venv venv
   ```

2. Activate it:

   ### Windows

   ```
   .\venv\Scripts\activate
   ```

   ### Mac/Linux

   ```bash
   source venv/bin/activate
   ```

3. Install all dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the script:

   ```bash
   python manage.py runserver
   ```

5. When you are done with the virtual environment, deactivate it by using:

   ```bash
   deactivate
   ```

## Frontend

While starting just the Django app does let you interact with the app, it uses the latest _build_ project in the frontend.
To run the frontend, you need to have [Node.js](https://nodejs.org/en/) installed in your machine. You can check if it is installed by running `node --version` and `npm --version`.
To develop frontend without having to rebuild the project every time, open another terminal and use the following commands:

Enter frontend folder

```bash
cd frontend
```

Install dependencies

```bash
npm ci
```

Start development app

```bash
npm start
```

Access `localhost:3000` to see the app in the browser.

phac@cpho2
