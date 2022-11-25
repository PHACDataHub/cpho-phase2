FROM dpage/pgadmin4:5.2

ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_PORT

# Switch to root to install new packages
USER 0

RUN apk update && apk add jq && cat /etc/passwd

COPY servers.json /servers.json

RUN \
  cat /servers.json | \
  DB_NAME=${DB_NAME} DB_USER=${DB_USER} DB_PASSWORD=${DB_PASSWORD} DB_HOST=${DB_HOST} DB_PORT=${DB_PORT} \
  jq ' \
    .Servers."1".Username=env.DB_USER | \
    .Servers."1".Port=env.DB_PORT | \
    .Servers."1".Host=env.DB_HOST | \
    .Servers."1".MaintenanceDB=env.DB_NAME \
  ' > /pgadmin4/servers.json && \
  chown 5050 /pgadmin4/servers.json && \
  echo "${DB_HOST}:${DB_PORT}:${DB_NAME}:${DB_USER}:${DB_PASSWORD}" > /pgpass && \
  chmod 0660 /pgpass

# Switch back to the pgadmin user (UID 5050)
USER 5050
