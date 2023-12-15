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

# Architecture (WIP):

![draft architecture](../architecture-diagram/architecture-k8s.svg)
