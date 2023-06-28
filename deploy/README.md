## Steps for initial deployment:
Note - this will be an iterative process streamlining this. A portion will likely end up as infrastruture as code.

1. Modify settings.py  
2. Authenticate 
    ```
    gcloud auth application-default login
    ```
2. Set project Variable
    ```
    gcloud config set project pdcp-cloud-006-cpho
    ```
3. Enable APIs and set up service accounts and secrets for Artifact Registry, Cloud Build trigger, Cloud Run and Cloud SQL.  Provision database. 
* Follow instructions in [deployment_gcloud_setup](deployment_gcloud_setup.sh) (run step by step in terminal or command prompt). 

* During first run through, when you're prompted with an error indication Cloud Build needs to be connected to the GitHub Repo:
    * Log into console to perform manual steps required for deployment set up
        * Cloud build connect to GitHub Repo
        * Artifact Registry - select 'Check for vunerabilities

4. Migrations - will be working with you on workflow - here are some possibilities: https://cloud.google.com/blog/topics/developers-practitioners/running-database-migrations-cloud-run-jobs

    Cloud SQL Proxy (Before Cloud Deploy for intial migrations on the first go):

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
    ```

5. Run migration (as outlined in [README.md](../README.md))

6. Deploy to Cloud Run - commit change to repo in triggered branch, or manually - comment out COMMITSHA from cloudbuild.yaml and:
    ```
    gcloud builds submit --config cloudbuild.yaml
    ``` 


