# CPHO server

This is a Django based API running GraphQL.

## Running the server

### Creating credentials

The server needs a database, and both need credentials so they can talk. Let's get that out of the way first.
Create some database credentials like so:
```sh
cat <<-'EOF' > postgres.env
POSTGRES_USER=cpho_user-admin
POSTGRES_PASSWORD=123
POSTGRES_DB=cpho_dev
EOF
```
And we'll need some matching credentials for the server itself:
```sh
cat <<-'EOF' > server.env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=cpho_dev
DB_USER=cpho_user-admin
DB_PASSWORD=123
DB_HOST=localhost
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

### Start the server

Assuming docker is installed, you can start postgres locally and run the migrations with the following command:

```sh
pdm dev
```

That script is a composite that runs `pdm db` then `pdm wait` to give it time to start, and follows that with `pdm migrate` and finally `pdm start`.
You can use them all separately if you like, and `pdm stop` is there when you're done.


## Managing dependencies

Dependencies are managed with [PDM](https://pdm.fming.dev/latest/). Mostly this will boil down to adding deps with `pdm add newdep`.
For compatibilitiy with the current docker-compose setup, after adding a new dependency you should regenerate the requirements.txt file with the following command:
```sh
pdm export --production --without-hashes -o requirements.txt
```
