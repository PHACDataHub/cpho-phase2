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


#########
# FINAL #
#########
# pull official base image
FROM python:3.10.6-alpine3.16

EXPOSE 8000 2222

# install dependencies
RUN apk add --no-cache libpq openssh su-exec

# create the appropriate directories, user and setup the ssh server
# ENV HOME=/cpho
# ENV APP_HOME=$HOME/web
ENV APP_HOME /app
WORKDIR $APP_HOME

ENV VIRTUALENV=$HOME/env
ENV WHEELDIR=$HOME/wheels
RUN \
    addgroup -S app && adduser --shell /bin/ash -u 5678 -S app -G app --home $HOME && \
    mkdir -p $APP_HOME && \
    mkdir $VIRTUALENV && \
    chown -R 5678 $HOME && \
    echo "root:Docker!" | chpasswd && \
    echo -e "CPHO Container\n\nFor management commands run: \nsu app\npython -m manage\n\n" > /etc/motd && \
    (cd /etc/ssh/ && ssh-keygen -A)

WORKDIR $APP_HOME

# change to the app user
# -- currently disabled due to needing sshd while in Azure  >:-(
# Instead the CMD passed to docker is ran using `su` via the entrypoint.
# USER 5678

# copy and install dependencies from build stage in virtual environment
COPY --chown=5678 --from=builder /usr/src/app/wheels $WHEELDIR
RUN python -mvenv $VIRTUALENV

ENV PATH="${VIRTUALENV}/bin:$PATH"

RUN echo -e "cd $APP_HOME\n" >> /etc/profile && \
    python -m pip install --no-cache $WHEELDIR/* && rm -rf $WHEELDIR

# copy project
COPY --chown=5678:app . $APP_HOME

# make entrypoint.prod.sh executable and create staticfiles dir (and files)
# RUN chmod +x $APP_HOME/entrypoint.prod.sh && \
RUN mkdir -p $APP_HOME/staticfiles 
# Create the staticfiles directory
# RUN mkdir -p /app/staticfiles

COPY ./static /$APP_HOME/staticfiles
# && \
# ENV SECRET_KEY=t ALLOWED_HOSTS=* DB_NAME=d DB_USER=d DB_PASSWORD=d DB_HOST=d DB_PORT=1 
# python -m manage collectstatic --no-input

# run entrypoint.prod.sh
# ENTRYPOINT ["/cpho/web/entrypoint.prod.sh"]
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "server.wsgi"]
CMD  exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 server.wsgi:application 
