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
    python3-dev

# Update pip
RUN pip install --upgrade pip

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt  

# TODO: this is a workaround, to be replaced when working out a proper data migration approach, possibly
# when using entrypoint.prod.sh to seed dat, need dev requirements installed. Also needed for testing.
COPY ./requirements_dev.txt .
COPY ./requirements_formatting.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements_dev.txt

#########
# FINAL #
#########
# pull official base image
FROM python:3.10.6-alpine3.16

ENV USER=5678

ENV HOME=/cpho
ENV APP_HOME=$HOME/web
ENV VIRTUALENV=$HOME/env
ENV WHEELDIR=$HOME/wheels

RUN \
    addgroup -S app && adduser --shell /bin/sh -u $USER -S app -G app --home $HOME && \
    mkdir -p $APP_HOME && \
    mkdir $VIRTUALENV && \
    chown -R $USER $HOME && \
    echo "root:Docker!" | chpasswd && \
    echo -e "CPHO Container\n\nFor management commands run: \nsu app\npython -m manage\n\n" > /etc/motd

WORKDIR $APP_HOME

# copy and install dependencies from build stage in virtual environment
COPY --chown=$USER --from=builder /usr/src/app/wheels $WHEELDIR

RUN python -mvenv $VIRTUALENV
ENV PATH="${VIRTUALENV}/bin:$PATH"

RUN echo -e "cd $APP_HOME\n" >> /etc/profile && \
    python -m pip install --no-cache $WHEELDIR/* && rm -rf $WHEELDIR

# copy project
COPY --chown=$USER:app . $APP_HOME

# Create a directory for the coverage report
RUN mkdir -p /cpho/web/coverage
# Set the directory permissions to allow writing
RUN chown -R $USER /cpho/web/coverage

# change to the app user
USER $USER

EXPOSE 8080

# Entrypoint script to run on-start steps (confirm migrations, etc)
ENTRYPOINT ["sh", "./entrypoint.prod.sh"]
CMD exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0 server.wsgi:application
