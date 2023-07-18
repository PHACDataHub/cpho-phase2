CREATE ROLE cpho_db_user WITH LOGIN PASSWORD '';
ALTER ROLE cpho_db_user CREATEDB;
CREATE DATABASE cpho_dev_db WITH OWNER cpho_db_user;
