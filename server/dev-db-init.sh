#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

# ----- Get environment variables  -----
source $(dirname "${BASH_SOURCE[0]}")/.env.dev
POSTGRES_USER=postgres

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER"  <<-EOSQL
	CREATE USER $DB_USER;
	CREATE DATABASE $TEST_DB_NAME;
	GRANT ALL PRIVILEGES ON DATABASE $TEST_DB_NAME TO $DB_USER;
EOSQL

# # cat .env.dev

# # Create "cpho_db_user" role if not exists
# if ! psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$DB_NAME" -tAc "SELECT 1 FROM pg_roles WHERE rolname='cpho_db_user'" | grep -q 1; then
#     # Role does not exist - create it
#     psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$DB_NAME" <<-EOSQL
#         CREATE ROLE cpho_db_user WITH LOGIN PASSWORD '';
#         ALTER ROLE cpho_db_user CREATEDB;
# EOSQL
#     echo "Creating cpho_db_user role"
# else 
#     echo "cpho_db_user role already exists."
# fi

# # Create "cpho_dev_db" if not exists
# if ! psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$DB_NAME" -lqt | cut -d \| -f 1 | grep -qw "cpho_dev_db"; then
#     # Database does not exist, so create it
#     psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$DB_NAME" <<-EOSQL
#         CREATE DATABASE cpho_dev_db WITH OWNER cpho_db_user;
# EOSQL
#     echo "Created cpho_dev_db database."
# else
#     echo "cpho_dev_db database  already exists."
# fi
