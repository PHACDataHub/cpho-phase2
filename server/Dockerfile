#################
# WHEEL BUILDER #
#################
FROM python:3.10.6-alpine3.16 as wheel_builder

# set work directory
WORKDIR /wheels

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

# build prod dependencies in /wheels/prod
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir ./prod -r requirements.txt  

# build dev-test dependencies in /wheels/dev-test
COPY ./requirements_dev.txt .
COPY ./requirements_formatting.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir ./dev-test -r requirements.txt -r requirements_dev.txt -r requirements_formatting.txt

#########
# FINAL #
#########
FROM python:3.10.6-alpine3.16

ENV USER=5678

ENV HOME=/cpho
ENV APP_HOME=$HOME/web
ENV VIRTUALENV=$HOME/env
ENV WHEELDIR=$HOME/wheels

RUN apk update && apk add postgresql14-client

RUN \
    addgroup -S app && adduser --shell /bin/sh -u $USER -S app -G app --home $HOME && \
    mkdir -p $APP_HOME && \
    mkdir $VIRTUALENV && \
    chown -R $USER $HOME && \
    echo "root:Docker!" | chpasswd && \
    echo -e "CPHO Container\n\nFor management commands run: \nsu app\npython -m manage\n\n" > /etc/motd

WORKDIR $APP_HOME

RUN python -mvenv $VIRTUALENV
ENV PATH="${VIRTUALENV}/bin:$PATH"

# copy and install dependencies from build stage in virtual environment
# choice of "prod" or "dev-test", corresponding to dependency directories from the wheel_builder step
ARG DEPENDENCY_SET="prod"
COPY --chown=$USER --from=wheel_builder /wheels/$DEPENDENCY_SET $WHEELDIR
RUN echo -e "cd $APP_HOME\n" >> /etc/profile && \
    python -m pip install --no-cache $WHEELDIR/* && rm -rf $WHEELDIR

# copy project
COPY --chown=$USER:app . $APP_HOME

# change to the app user
USER $USER

EXPOSE 8080

# Entrypoint script to run on-start steps (confirm migrations, etc)
ENTRYPOINT ["sh", "./entrypoint.prod.sh"]
# gunicorn configuration found in gunicorn.conf.py
CMD exec gunicorn
