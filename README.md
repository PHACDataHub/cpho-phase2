# CPHO Phase 2

[![Docker Image CI](https://github.com/PHACDataHub/cpho-phase2/actions/workflows/docker-image.yml/badge.svg)](https://github.com/PHACDataHub/cpho-phase2/actions/workflows/docker-image.yml)

## Note: This is _very much_ a work in progress. Work needs to be done to transform this prototype into an usable production application.

## How to run locally

These instructions are aimed at getting the whole system running for development purposes. The [frontend](frontend/README.md) and [server](server/README.md) folders contain details on running those specific services without Docker.

### Docker

You'll need to Install [Docker](https://docs.docker.com/install/) and have it running

### Creating credentials

We need server and database credentials to be created in the server folder:

```sh
cat <<-'EOF' > server/postgres.env
POSTGRES_USER=cpho_user-admin
POSTGRES_PASSWORD=123
POSTGRES_DB=cpho_dev
EOF
```

We'll need some matching credentials for the server.
To generate a secret key, you can use tools such as [RandomKeygen](https://randomkeygen.com) to generate a strong key.

```sh
cat <<-'EOF' > server/server.env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=cpho_dev
DB_USER=cpho_user-admin
DB_PASSWORD=123
DB_HOST=postgres
DB_PORT=5432
SECRET_KEY= # ADD GENERATED KEY HERE #
# PGADMIN CONTAINER
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=123
PGADMIN_LISTEN_PORT=5433
PGADMIN_CONFIG_SERVER_MODE=False
PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED=False
PGADMIN_CONFIG_UPGRADE_CHECK_ENABLED=False
EOF
```

### Running it!

Run `docker compose up -d` in the root directory of the project.

Docker should have created 4 containers:
- `pg_container`: PostgreSQL database
- `cpho_server_container`: Django Server
- `cpho_frontend_container`: React Frontend

Now, you can do the following:

- Navigate to `localhost:3000` to view the frontend
- Navigate to `localhost:8000/graphql` to view the GraphQL interface

When you're done working, you can run `docker compose down` to stop the containers

