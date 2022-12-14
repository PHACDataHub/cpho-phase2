# build stage
FROM python:3-alpine AS builder
# Add build dependencies
RUN apk add -U --no-cache libpq gcc python3-dev musl-dev postgresql-dev
# install PDM
RUN pip install pdm

WORKDIR /cpho
# copy project files in
COPY . .

# Install deps in ./__pypackages__ as per PEP 582
RUN pdm config python.use_venv False && pdm install --prod --no-lock --no-editable

# Build the production image
FROM python:3-alpine

# Make Python play nice with containers.
ENV PYTHONUNBUFFERED=1, PYTHONDONTWRITEBYTECODE=1
# Tell the interpreter where to look to resolve import statements.
ENV PYTHONPATH=/home/nonroot/cpho/__pypackages__/3.11/lib

# Add a nonroot user for running our process
RUN addgroup -S nonroot && adduser -S nonroot -G nonroot

# Install the runtime dependency of psycopg
RUN apk add -U --no-cache libpq

# Retrieve packages from build stage
COPY --from=builder /cpho/__pypackages__ /home/nonroot/cpho/__pypackages__
# Copy in the code as well
COPY --from=builder /cpho /home/nonroot/cpho
COPY --from=builder /cpho/server.py /home/nonroot/cpho/server.py

WORKDIR /home/nonroot/
# Run the process with a nonroot user
USER nonroot
# Run the app with Waitress:
CMD ["python", "cpho/server.py"]
