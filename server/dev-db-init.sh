#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

# Get environment variables
source $(dirname "${BASH_SOURCE[0]}")/.env.dev

# Set default password
POSTGRES_USER=postgres

# Create DB user and database for dev and testing. 
echo "Create $DB_USER role and $DB_NAME database"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER"  <<-EOSQL
    CREATE ROLE $DB_USER WITH LOGIN;
	ALTER ROLE $DB_USER CREATEDB;
	createdb -U "$DB_USER" "$DB_NAME"
EOSQL

