## Steps for initial deployment:
Note - there will be an iterative process streamlining this. A portion will likely end up as infrastructure as code, for reuse on generic Django apps. 

1. Authenticate your PHAC GCP user account (note: going to assume this user has access to the relevant GCloud project)
    ```
    gcloud auth login
    ```

2. Update values in [`gcloud_env_var.sh`](gcloud_env_var.sh). Generally, you'll only need to touch the `PROJECT_ID` value

3. Run [`gcloud_init_setup.sh`](gcloud_init_setup.sh), follow the prompts

6. Run initial migrations and DB population (as outlined in the repo root [README.md](../README.md)). Two suggested ways to do this:
    * Via cloud build:
        * temporarily add necessary dependencies to the `../server/Dockerfile`
        * temporarily add seeding steps to `../server/entrypoint.prod.sh`
        * manually run the Cloud Build job via `gcloud builds submit --config cloudbuild.yaml --substitutions COMMIT_SHA="local$(date +%s)"`
        * revert dockerfile and entryoint script

    * Via Cloud SQL Proxy: (TODO this might not be an option with the current network configuration)
        * follow [this](https://cloud.google.com/sql/docs/postgres/sql-proxy) guide to install Cloud SQL Proxy and use it to connect to the database from your dev machine
        * run the necessary migration and seeding commands/scripts locally

7. Deploy to Cloud Run (if necessary)
    * if the GitHub repo is connected and the trigger configured, just push a commit
    * otherwise, trigger manually with `gcloud builds submit --config cloudbuild.yaml --substitutions COMMIT_SHA="local$(date +%s)"`
