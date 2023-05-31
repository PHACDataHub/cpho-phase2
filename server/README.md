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

And we'll need some matching credentials for the server itself (don't forget to add a generated key from a website like [RandomKeygen](https://randomkeygen.com)):

```sh
cat <<-'EOF' > server/.env
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

### Start the server

Assuming [Docker](https://docs.docker.com/install/) and [PDM](https://pdm.fming.dev/latest/) are installed, run the following to [make pep582 packages available](https://pdm.fming.dev/latest/usage/pep582/#enable-pep-582-globally):

Windows

```sh
pdm --pep582
```

Linux

```sh
pdm --pep582 >> ~/.bash_profile
```

Then, you can install the dependencies as follows:

```sh
pdm install
```

Then, you can start postgres locally and run the migrations with the following command:

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
