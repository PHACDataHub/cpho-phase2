# Resource organization
All kubernetes resources are arranged under the `k8s/` directory. Every sub-directory within `k8s/` corresponds to a name of the kubernetes namespace, i.e, resources provisioned in the same namespace are stored together. For example, all resources for the `flux-system` namespace are stored in the `k8s/flux-system` directory.

Every sub-directory is expected to have a `sync.yaml` and a `kustomization.yaml` (from `kustomize.config.k8s.io/v1beta1` and not `kustomize.toolkit.fluxcd.io/v1`) that work together to enable reconciliations in flux. Currently, all resources in the `sync.yaml` are provisioned in the `flux-system` namespace. You can think of the `sync.yaml` as an entrypoint to a namespace / micro-service. It contains reconciliation mechanisms pertianing to any git repo / kustomize / image repo / image automation etc.

Most of the `sync.yaml` (`kustomize.toolkit.fluxcd.io/v1`) resources have a `depends_on` key that enables a user to specify dependencies between kustomizations. This is particulary useful when deploying applications from scratch. For instance, the `cert-manager` CRDs must be available and ready to use in the cluster prior to the deployment of certificate and issuer resources. To achieve this, the `cert-manager-resources` kustomization has a dependency on `cert-manager-crds`; see `k8s/cert-manager/sync.yaml` for reference.

# Setup

## Configuring Flux
Assuming that the necessary GCP resources have been provisioned and configured, kubernetes resources can be deployed by first configuring Flux with:

```
flux bootstrap git \
  --author-email=<your.email> \
  --url=ssh://git@github.com:PHACDataHub/cpho-phase2.git \
  --branch=main \
  --path=k8s/ \
  --components-extra="image-reflector-controller,image-automation-controller"
```

More information on `flux bootstrap git` [here](https://fluxcd.io/flux/cmd/flux_bootstrap_git/).

This will install flux on your cluster and, at some point during the process, will ask you to add the deploy key (printed on your terminal) to github. More information on how to add a deploy key to your repo [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys#set-up-deploy-keys).

The above command installs all manifests under `k8s/flux-system` directory.

## Encrypting secrets

We use [SOPS](https://github.com/getsops/sops) with [GCP KMS](https://cloud.google.com/kms/docs#docs) to encrypt secrets and store them in git. The workflow then is to [create a kubernetes secret definition](https://kubernetes.io/docs/concepts/configuration/secret/#creating-a-secret) and encrypt it with:

```sh
sops -e <path/to/secret.yaml> > <path/to/encrypted/secret.yaml>
```

> If you run into a `reauth_related_error` use `gcloud config set project pht-01hp04dtnkf` to set the project id and then run `gcloud auth application-default login` to refresh the auth token.

To decrypt use:

```sh
sops -d <path/to/encrypted/secret.yaml>
```

> Note: You'll need the [SOPS CLI](https://github.com/getsops/sops?tab=readme-ov-file#11stable-release) binary to run the above commands.

The `kustomize-controller` pod is [configured to automatically depcrypt](https://fluxcd.io/flux/guides/mozilla-sops/#google-cloud) an encrypted kubernetes secret when it gets reconciled with flux. However, note that it can only decrypt secrets when the flux kustomization sync manifest has `spec.decryption.provider` set to `sops` (See [this](https://github.com/PHACDataHub/cpho-phase2/blob/main/k8s/flux-system/gotk-sync.yaml#L16-L30) for an example).

> Note: Currently, only the `server-django` and `flux-system` kustomization resources have `spec.decryption.provider` set.

Information such as which key / method to use during encryption / decryption comes from the `.sops.yaml` file at the root of this repo. Moreover, instead of the full manifest only `data` / `stringData` fields of the kubernetes secret should be encrypted. `.sops.yaml` automatically takes care of this via it's `encrypted_secret` field when you run the above commands from the root of this repo.

## Installing other resources

As mentioned earlier, the `sync.yaml` serves as an entrypoint to the resources in a particular namespace and can be added to the cluster with:

```
kubectl apply -f <path/to/directory>/sync.yaml
```
where `<path/to/directory>` could be, for example, `k8s/istio-ingress/sync.yaml` which would install / configure all resources under the `istio-system` namespace or more specifically all resources as per the `k8s/istio-ingress` directory's `kustomization.yaml`.

Since there are dependencies between resources, the above command must be executed for each namespace in a certain order. At the time of writing, the order is:
- `flux-system`: Flux and sealed-secrets CRDs and resources. 
- `istio-ingress`: Ingress configurations. Requires update to the ip address in the directory's `kustomization.yaml`.
- `cert-manager`: Cert-Manager crds and resources. Requires update to the domain names, project id, etc. at relevant places in the manifests.
- `cnpg-system`: Cloud-Native Postgres crds and configurations.
- `server`: Application and PostgresDB Cluster manifests

# Postgres Cluster Backup and Recovery
> **Note:** Except for `./server/postgres/backup/scheduled.yaml`, none of the other resources linked in this section are synced with flux.

## Backup

There are two ways to back up the cluster:

- Scheduled
  - [Spec](https://github.com/PHACDataHub/cpho-phase2/blob/main/k8s/server/postgres/backup/scheduled.yaml)
    
    This is done automatically as per `0 0 0 * * *` cron schedule and is synced with flux.
  - [Official Doc](https://cloudnative-pg.io/documentation/1.21/backup/#scheduled-backups)

- On-demand
  - [Spec](https://github.com/PHACDataHub/cpho-phase2/blob/main/k8s/server/postgres/backup/on-demand.yaml)
    
    This can applied to the cluster like any other k8s resource with:
    ```sh
    kubectl apply -f k8s/server/postgres/backup/on-demand.yaml
    ```
  - [Official doc](https://cloudnative-pg.io/documentation/1.21/backup/#on-demand-backups)

## Recovery

There are three ways to do this:
- From object storage
  
  This uses a K8 service account with `metadata.name` to recover the data. Ensure that the `workloadIdentityUser` role is assigned to the cloud service account with the right namespace and K8s service account name.
  - [Spec](https://github.com/PHACDataHub/cpho-phase2/blob/main/k8s/server/postgres/restore/restore-from-object-storage.yaml)
  - [Official doc](https://cloudnative-pg.io/documentation/1.21/recovery/#recovery-from-an-object-store)

- From K8s backup resource
  - [Spec](https://github.com/PHACDataHub/cpho-phase2/blob/main/k8s/server/postgres/restore/restore-from-k8s-backup-object.yaml)
  - [Official doc](https://cloudnative-pg.io/documentation/1.21/recovery/#recovery-from-a-backup-object)

- From live cluster
  - [Spec](https://github.com/PHACDataHub/cpho-phase2/blob/main/k8s/server/postgres/restore/restore-from-live-cluster.yaml)
  - [Official doc](https://cloudnative-pg.io/documentation/1.21/bootstrap/#bootstrap-from-a-live-cluster-pg_basebackup)

# Maintenance

**TODO:** Automate maintenance tasks with Github Actions. [Here's](https://fluxcd.io/flux/flux-gh-action/) a reference implementation for Flux. Similar approach can be followed for other components.

## Upgrading Flux

To [upgrade flux](https://fluxcd.io/flux/installation/upgrade/) on the cluster, first make sure you have the latest [Flux CLI](https://fluxcd.io/flux/cmd/). Run the following command from the root of this repository and submit a PR with changes:

```sh
flux install \
  --components-extra image-reflector-controller,image-automation-controller \
  --components="source-controller,kustomize-controller,notification-controller" \
  --export > ./k8s/flux-system/gotk-components.yaml
```

Once the PR is merged, Flux will propagate the changes. See the [official releases](https://github.com/fluxcd/flux2/releases) page for more information regarding an upgrade.

## Upgrading Cert-manager

To [upgrade cert-manager](https://cert-manager.io/docs/installation/upgrade/) on the cluster, run the following command from the root of this repository and submit a PR with changes:

```sh
curl -sSL https://github.com/cert-manager/cert-manager/releases/download/<VERISON>/cert-manager.yaml > ./k8s/cert-manager/crds/cert-manager.yaml
```
> Replace `<VERISON>` with a valid cert-manager CRD version.

Once the PR is merged, Flux will propagate the changes. See the [official releases](https://cert-manager.io/docs/releases/) page for more information regarding an upgrade.

## Upgrading Config Connector:

To [upgrade config connector](https://cloud.google.com/config-connector/docs/how-to/install-manually#upgrading) on the cluster, run the following commands from the root of this repository and submit a PR with changes:

```sh
gsutil cp gs://configconnector-operator/<VERSION>/release-bundle.tar.gz release-bundle.tar.gz
tar zxvf release-bundle.tar.gz
cp ./operator-system/autopilot-configconnector-operator.yaml ./k8s/configconnector-operator-system/
rm -rf operator-system/ release-bundle.tar.gz
```
> Replace `<VERISON>` with a valid KCC Operator version.

Once the PR is merged, Flux will propagate the changes. See the [official releases](https://github.com/GoogleCloudPlatform/k8s-config-connector/releases) page for more information regarding an upgrade.

## Upgrading PostgreSQL:

There are two types of updates in this section:
- Upgrading the operator
- Updating the image

### Operator

To [upgrade cnpg operator](https://cloudnative-pg.io/documentation/current/installation_upgrade/#upgrades) on the cluster, run the following commands from the root of this repository and submit a PR with changes:

```sh
curl -sSL https://github.com/cloudnative-pg/cloudnative-pg/releases/download/v<VERISON>/cnpg-<VERSION>.yaml > ./k8s/cnpg-system/cnpg-crds.yaml
```
> Replace `<VERISON>` with a valid CNPG Operator version.

Once the PR is merged, Flux will propagate the changes. See the [official releases](https://github.com/GoogleCloudPlatform/k8s-config-connector/releases) page for more information regarding an upgrade.

### Image

Replace the PostgreSQL image tag at `spec.imageName` in the `./k8s/server/base/postgres/pg-cluster.yaml`. Valid images can be found [here](https://github.com/cloudnative-pg/postgres-containers/pkgs/container/postgresql).

See the [official documentation](https://cloudnative-pg.io/documentation/1.22/#container-images) for more info on PostgreSQL images.

# Ephemeral Environments

Ephemeral environments for the Django server and PostgreSQL database i.e, `server` namespace are implemented using kustomize and Flux. The `./k8s/server` directory is organized into [kustomize bases and overlays](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/#bases-and-overlays). The overlays are further divided into `prod` and `ephemeral` directories that contain kubernetes configurations for production and ephemeral environments respectively.

The `prod` directory syncs (as per the configuration [here](https://github.com/PHACDataHub/cpho-phase2/blob/prod/k8s/server/overlays/prod/sync.yaml)) against the `prod` branch of the repository and serves traffic at `hopic-sdpac.data-donnes.phac-aspc.gc.ca`. On the other hand, the `ephemeral` directory syncs (as per the configuration(s) [here](https://github.com/PHACDataHub/cpho-phase2/tree/prod/k8s/server/ephemeral-instances)) against any branch that is configured to use ephemeral environments and serves traffic at `*.dev.hopic-sdpac.data-donnes.phac-aspc.gc.ca`, where `*` is replaced by the github branch name that the environment is built from. 

As an example, suppose you need an ephemeral environment on a branch called `dev-test`. The first step would be to create that branch with -

```sh
git checkout -b dev-test
```

> Note: It is recommended to take a fresh pull and use the `prod` branch as base because at any point it'll contain the most updated kubernetes manifests.

Once the branch is created; checkout back to `prod` with:

```sh
git checkout prod
```

Now, copy over the sync configuration from `./k8s/server/overlays/ephemeral/sync-template.yaml` and paste it in a new file called `dev-test-sync.yaml` inside the `./k8s/server/ephemeral-instances/` directory. Replace all occurences of `${BRANCH_NAME}` with the name of the branch, in this case, `dev-test`.

> In general, all ephemeral flux syncs are stored at the `./k8s/server/ephemeral-instances/` location.

Submit a PR against `prod` with the changes you just made -

```sh
git checkout -b add-ephemeral-dev-test
git add ./k8s/ephemeral-instances/
git commit -m "feat: add ephemeral env for dev-test"
git push
```

> Note how the branch name in the checkout command above is different from the branch name you need an ephemeral environment in.

Once the PR is merged, Flux will propagate the changes i.e, create the ephemeral environment using kubernetes manifests from the `dev-test` branch's `./k8s/server/overlays/ephemeral/` directory.

## Deleting an ephemeral environment

To delete an ephemeral environment from the cluster, simple delete the branch's sync file from the `./k8s/server/ephemeral-instances` directory. For instance, to clean up the ephemeral environment for `dev-test` branch, delete the `./k8s/server/ephemeral-instances/dev-test-sync.yaml` file.

## Gotchas

- Cloudbuild is only available on the `prod` branch. To enable image builds from your branch, update the `GITHUB_MAIN_BRANCH_NAME` variable with the name of your branch in `./deploy/gcloud_env_vars.sh` file.
  Here's a diff from the `dev-test` example above for reference:
  ```sh
  diff --git a/deploy/gcloud_env_vars.sh b/deploy/gcloud_env_vars.sh
  index c861c4d..45361ce 100755
  --- a/deploy/gcloud_env_vars.sh
  +++ b/deploy/gcloud_env_vars.sh
  @@ -19,7 +19,7 @@ export PROJECT_ALPHA_SUB_DOMAIN=hopic-sdpac
   export BUILD_GITHUB_REPO_NAME=cpho-phase2
   export BUILD_GITHUB_REPO_OWNER=PHACDataHub

  -export GITHUB_MAIN_BRANCH_NAME=prod
  +export GITHUB_MAIN_BRANCH_NAME=dev-test

   export TEST_COVERAGE_BUCKET_NAME=hopic-test-coverage-reports-01hp04dtnkf
   export TEST_COVERAGE_THRESHOLD=77.5 # set just below current coverage, consider increasing in time
  ```

- The ephemeral environment is completely isolated from the production deployment in it's own kubernetes namespace. The name of the kubernetes namespace is the same as the github branch name that the environment is to be built from.

- The database cluster for an ephemeral environment is currently built from the most recent (at the time of ephemeral env creation) backup of the production cluster stored in the cloud storage.
  > This might change in the future when we've figured out a way to seed the DB with fake data.

- The `./k8s/overlays/ephemeral/infrastructure` grants necessary permissions for the ephemeral environment's database cluster to access the cloud storage bucket. See https://github.com/PHACDataHub/cpho-phase2/pull/205 for details on why this is required.

- By default, automation for updating the server deployment image when a new one is available in the registry won't work with ephemeral deployments. In order to configure it, you must edit the `$imagepolicy` comment with the ephemeral `ImagePolicy` resource name at `spec.template.spec.image` in the `./k8s/server/overlays/ephemeral/django/deployment.yaml` file **in your branch**.
  
  Taking `dev-test` as an example, here's what the diff looks like:
  ```
  diff --git a/k8s/server/overlays/ephemeral/django/deployment.yaml b/k8s/server/overlays/ephemeral/django/deployment.yaml
  index a082484..9495c89 100644
  --- a/k8s/server/overlays/ephemeral/django/deployment.yaml
  +++ b/k8s/server/overlays/ephemeral/django/deployment.yaml
  @@ -7,7 +7,7 @@ spec:
       spec:
         containers:
         - name: server
  -        image: northamerica-northeast1-docker.pkg.dev/pht-01hp04dtnkf/hopic-k8s-images/cpho-phase2:prod-fa2312df-1708014514 # {"$imagepolicy": "flux-system:server"}
  +        image: northamerica-northeast1-docker.pkg.dev/pht-01hp04dtnkf/hopic-k8s-images/cpho-phase2:prod-fa2312df-1708014514 # {"$imagepolicy": "flux-system:dev-test-server"}
           resources:
             # Autopilot only considers requests (see https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-resource-requests#resource-limits)
             requests:
  ```
  
  Note that the `$imagepolicy` comment is updated to `dev-test-server`. In general the value for this will be `${BRANCH_NAME}-server`, where `${BRANCH_NAME}` is the name of the ephemeral env branch.

  > The name of the image policy is contained in the `metadata.name` field of the `ImagePolicy` resource in the `dev-test-sync.yaml` file.

# Architecture

This deployment architecture is built on top of the [node-microservices-demo](https://github.com/PHACDataHub/node-microservices-demo?tab=readme-ov-file#node-microservices-demo) i.e, the rationale for implementing such an architecture can be found in the embedded link. Here's a detailed diagram that outlines all of the components and their interactions:

> Stroke colors are used to represent operational flows.
>  - Red: Unauthenticated traffic
>  - Green: Authenticated traffic
>  - Orange: Certificate Management
>  - Grey: Django deployment
>  - Black: PostgreSQL deployment
>  - Gold: Notification
>  - Blue: CI/CD
>  - Sky Blue: Observability

![Current k8s architecture](../architecture-diagram/architecture-k8s.svg)

> See `./architecture-diagram/README.md` at the root of this repository for other diagrams.

## How are the changes deployed?

TLDR; GitOps

Once a change is merged into `prod`, the cloudbuild trigger executes the CI pipeline that runs tests, uploads coverage reports to the cloud storage bucket and, builds, tags and pushes an image to the artifact registry. The image tags follow a naming convention of - `${branch_name}-${short_sha}-$(date +%s)`. See `./cloudbuild.yaml` at the root of this repo for details about the CI pipeline.

Flux scans the image repository for new tags based on a regex pattern (see [spec](https://github.com/PHACDataHub/cpho-phase2/blob/update-readme/k8s/server/overlays/prod/sync.yaml#L50-L58)) that matches the naming convention mentioned previously, and pushes an update on GitHub to the kubernetes deployment manifest (based on the `$imagepolicy` comment) with the new image tag.

In addition to scanning the image repository, Flux also scans the Git repository (see [spec](https://github.com/PHACDataHub/cpho-phase2/blob/prod/k8s/flux-system/gotk-sync.yaml#L3-L14)) for changes and continously reconciles manifests to the kubernetes cluster. Due to this, the "[updated image tag](https://github.com/PHACDataHub/cpho-phase2/commit/efd626a010627f6f925f949b2242f776d83d6405)" commit is seen by Flux and is then _pulled_ into the cluster to be applied; therefore, [rolling out](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/) a new version of the application.  

## How is infrastructure created / managed?

Google's config connector, an open source kubernetes add-on, is used to manage cloud infrastructure via kubernetes. All infrastructure definitions are stored in the `./infrastructure` directory at the root of this repository. Like all other kubernetes manifests, this directory too is reconciled continously to the cluster by Flux.

There are two reconciliation mechanisms at play here:
- **Git repo to Cluster**: Managed by Flux
- **Cluster to Google Cloud**: Managed by config connector i.e, the resources on the cloud are reconciled against their kubernetes resource counterparts.

Checkout the [official documentation](https://cloud.google.com/config-connector/docs/overview) for more details about config connector.

## What's the use case for each of these components?

- **Flux**: Reconcile kubernetes manifests from the git repository to the cluster. 
- **Cert-manager**: Provision and manage the life cycle of TLS certificates within the kubernetes cluster.
- **CNPG (Cloud-native Postgres) Operator**: Manages PostgreSQL workloads on the cluster, thereby relying on kubernetes for capabilities like self-healing, replication, high availability, backup, recovery, updates, etc.
- **Config Connector**: To manage cloud infrastructure within kubernetes.
- **Anthos Service Mesh (Managed Istio)**: Configures secure networking for the cluster by providing L7 traffic management and mTLS capabilities.

# Gotchas

- The current GKE autopilot cluster is binded to a [fleet](https://cloud.google.com/anthos/fleet-management/docs) in the `php-fleet-monitoring` project. As a result, some enterprise features might be visible only in the `php-fleet-monitoring` project's space. This is to have a single pane of glass for kubernetes clusters.
- Some cloud resources, specifically the cloud storage bucket and KMS, have a special annotation (`cnrm.cloud.google.com/deletion-policy: abandon`) set to prevent deletion of cloud resources if the cluster goes down. See https://github.com/PHACDataHub/cpho-phase2/pull/221 for further details.
- Flux sends reconciliation alerts to the slack channel, however, [some of these alerts](https://github.com/PHACDataHub/cpho-phase2/blob/prod/k8s/flux-system/alerts/alerts.yaml#L37-L47) are ignored due to https://github.com/PHACDataHub/cpho-phase2/pull/208.
- Not all infrastructure is expressed in the `./infrastructure` directory, some of it is contained in the `./k8s/Taskfile.yaml`. This is due to https://github.com/PHACDataHub/cpho-phase2/pull/193#issue-2121787136.
