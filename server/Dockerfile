###########
# BUILDER #
###########
FROM python:3.10.6-alpine3.16 as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk update \
    && apk add  \
    gcc \
    libffi-dev \
    musl-dev \
    openssl-dev \
    postgresql-dev \
    python3-dev \
    bash

# Update pip
RUN pip install --upgrade pip

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#################
# SECRET READER #
#################
FROM google/cloud-sdk:437.0.1 as secret_reader

# set work directory
WORKDIR /usr/src/app

COPY ./key.json ./key.json
RUN gcloud auth activate-service-account --key-file ./key.json

COPY ./deploy ./deploy
RUN ./deploy/make_prod_env_file.sh


#########
# FINAL #
#########
# pull official base image
FROM python:3.10.6-alpine3.16

EXPOSE 8000 2222

ENV USER=5678

ENV HOME=/cpho
ENV APP_HOME=$HOME/web
ENV VIRTUALENV=$HOME/env
ENV WHEELDIR=$HOME/wheels

RUN \
    addgroup -S app && adduser --shell /bin/bash -u $USER -S app -G app --home $HOME && \
    mkdir -p $APP_HOME && \
    mkdir $VIRTUALENV && \
    chown -R $USER $HOME && \
    echo "root:Docker!" | chpasswd && \
    echo -e "CPHO Container\n\nFor management commands run: \nsu app\npython -m manage\n\n" > /etc/motd

WORKDIR $APP_HOME

# change to the app user
USER $USER

# copy and install dependencies from build stage in virtual environment
COPY --chown=$USER --from=builder /usr/src/app/wheels $WHEELDIR
RUN python -mvenv $VIRTUALENV
ENV PATH="${VIRTUALENV}/bin:$PATH"
RUN echo -e "cd $APP_HOME\n" >> /etc/profile && \
    python -m pip install --no-cache $WHEELDIR/* && rm -rf $WHEELDIR

# copy project
COPY --chown=$USER:app . $APP_HOME

# Get prod env var file from secret_reader step and run collect static as container build time steps; both should be immutable to the deployed image
COPY --chown=$USER --from=secret_reader /usr/src/app/.env.prod $APP_HOME/server
RUN python manage.py collectstatic --no-input

# entrypoint script to run on-start steps (confirm migrations, etc)
ENTRYPOINT ["/cpho/web/entrypoint.prod.sh"]
CMD exec gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 8 --timeout 0 server.wsgi:application
