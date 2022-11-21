# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11.0-buster

ENV PORT_NUM=8000


# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install NC and locales
RUN \
  apt-get update && \
  apt-get install -y netcat locales libpq-dev

# Add Canadian locales
RUN \
  sed -i -e 's/# en_CA.UTF-8 UTF-8/en_CA.UTF-8 UTF-8/' /etc/locale.gen && \
  sed -i -e 's/# fr_CA.UTF-8 UTF-8/fr_CA.UTF-8 UTF-8/' /etc/locale.gen && \
  dpkg-reconfigure --frontend=noninteractive locales

WORKDIR /server

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN \
  adduser -u 5678 --disabled-password --gecos "" appuser && \
  mkdir /env && \
  chown appuser /env

USER 5678

# Install pip requirements
COPY requirements.txt ./
RUN \
  python -mvenv /env && \
  /env/bin/python -m pip install -r requirements.txt


# Make our virtual env the default python
ENV PATH="/env/bin:$PATH"

# Set the TMP variable to move pytest_cache outside of our working directory
ENV TMP=/tmp

# run entrypoint.sh
ENTRYPOINT ["/server/entrypoint.sh"]

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
