## Steps for initial deployment:
Note - there will be an iterative process streamlining this. A portion will likely end up as infrastructure as code, for reuse on generic Django apps. 

0. TODO: updates to project Dockerfile, settings.py, and .env file pending, before everything deploys and works as expected. We'll work those out as we go

1. Authenticate your PHAC GCP user account (note: going to assume this user has access to the relevant GCloud project)
    ```
    gcloud auth login
    ```

2. Update values in [`gcloud_env_var.sh`](gcloud_env_var.sh), set relevant project ID, etc. Many may not need to change

3. Run [`gcloud_init_setup.sh`](gcloud_init_setup.sh), follow the prompts

6. Run initial migrations and DB population (as outlined in the repo root [README.md](../README.md)). Migrations can be run a number of ways, prod-ready approach TBD, but here are some options for now: 
    * (As a cloud run job)[https://cloud.google.com/blog/topics/developers-practitioners/running-database-migrations-cloud-run-jobs]

    * From your dev machine via Cloud SQL Proxy:
        * Download [Cloud SQL Proxy](https://cloud.google.com/sql/docs/postgres/sql-proxy) 
            This is for connecting to Cloud SQL from your computer for initial set up 
        * [Link to curl command to download & install](https://cloud.google.com/sql/docs/postgres/sql-proxy#install)
        
            ```
            chmod +x cloud-sql-proxy 
            ```
            * Run app locally with cloud sql proxy (note this is for non-windows machines)(https://cloud.google.com/sql/docs/sqlserver/connect-instance-auth-proxy) for other devices 
            ```
            ./cloud-sql-proxy $PROJECT_ID:$REGION:$DB_INSTANCE_NAME
            ```
            Note: This seems to timeout - if you get oauth2: "invalid_grant" "reauth related error (invalid_rapt):
            ```
            gcloud auth application-default revoke
            ```
            ```
            gcloud auth application-default login

7. Deploy to Cloud Run. Either:
    - Cloud Build job triggered by commit, or
    - manually, comment out COMMITSHA from cloudbuild.yaml and run:
    ```
    gcloud builds submit --config cloudbuild.yaml
    ``` 


