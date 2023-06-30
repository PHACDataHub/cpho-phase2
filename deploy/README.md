## Steps for initial deployment:
Note - there will be an iterative process streamlining this. A portion will likely end up as infrastructure as code, for reuse on generic Django apps. 

0. TODO: updates to project Dockerfile, settings.py, and .env file pending, before everything deploys and works as expected. We'll work those out as we go

1. Authenticate your PHAC GCP user account (note: we assume you have access to the pdcp-cloud-006-cpho project)
    ```
    gcloud auth login
    ```

2. Set project and region
    ```
    gcloud config set project pdcp-cloud-006-cpho
    gcloud config set compute/zone northamerica-northeast1
    ```

3. Get Application Default Credentials, these will be used by default in subsequent API calls
    ```
    gcloud auth application-default login
    ```

4. Enable APIs and set up service accounts and secrets for Artifact Registry, Cloud Build trigger, Cloud Run and Cloud SQL.
    * Follow along with [deployment_gcloud_setup.sh](deployment_gcloud_setup.sh) (run step by step in terminal or command prompt, don't just execture the script). 

    * During first run through, when you're prompted with an error indication Cloud Build needs to be connected to the GitHub Repo:
        * Log into console to perform manual steps required for deployment set up
            * Cloud build connect to GitHub Repo
            * Artifact Registry - select 'Check for vulnerabilities'

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
            ./cloud-sql-proxy $PROJECT_ID:$REGION:$INSTANCE_NAME
            ```
            Note: This seems to timeout - if you get oauth2: "invalid_grant" "reauth related error (invalid_rapt):
            ```
            gcloud auth application-default revoke
            ```
            ```
            gcloud auth application-default login

7. Deploy to Cloud Run. Either:
    - Cloud Build job triggered by commit, or
    - manually - comment out COMMITSHA from cloudbuild.yaml and run:
    ```
    gcloud builds submit --config cloudbuild.yaml
    ``` 


