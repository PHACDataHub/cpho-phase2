# Flux

This folder contains the config needed to deploy the system with flux.
The config here was generated with the following commands:

```bash
# generate flux crds with only the features we use
flux install --export --components=source-controller,kustomize-controller,notification-controller --components-extra 'image-reflector-controller,image-automation-controller' > crds.yaml
# Tell flux what repo and branch to watch
flux create source git github-repo --export --branch main --url "ssh://github.com/PHACDataHub/cpho-phase2.git" > flux/github-repo.yam
# tell flux to `kustomize build | kubectl apply` the ingress folder for that repo
flux create kustomization ingress --export --path istio --source github-repo > flux/ingress-kustomization.yaml
# tell flux to `kustomize build | kubectl apply` the frontend folder after istio starts
# Istio needs to be running for it to inject sidecar containers
flux create kustomization frontend --export --path frontend --source github-repo --health-check=Deployment/istio-ingressgateway.istio-ingress > flux/frontend-kustomization.yaml
# Automate image updates. Start by creating an updater:
flux create image update --export --namespace flux-system --git-repo-ref=github-repo --checkout-branch main --author-name fluxbot --author-email fluxcd@users.noreply.github.com --commit-template '[ci skip] {{range .Updated.Images}}{{println .}}{{end}}' cpho-automation > image-update-automation.yaml
# Then we need to tell flux what images to watch
flux create --export image repository server --image=northamerica-northeast1-docker.pkg.dev/pdcp-cloud-006-cpho/cpho/server > server-image-repository.yaml
flux create --export image repository frontend --image=northamerica-northeast1-docker.pkg.dev/pdcp-cloud-006-cpho/cpho/frontend > frontend-image-repository.yaml
# Create image policies for how they are updated
flux create --export image policy server --image-ref=server --select-alpha=asc --filter-regex='^main-[a-f0-9]+-(?P<ts>[0-9]+)' --filter-extract='$ts' > server-image-policy.yaml
flux create --export image policy frontend --image-ref=frontend --select-alpha=asc --filter-regex='^main-[a-f0-9]+-(?P<ts>[0-9]+)' --filter-extract='$ts' > frontend-image-policy.yaml
```

Generating deploy keys for flux looks like this:

```bash
mkdir deploy
kubectl create namespace flux-system -o yaml --dry-run=client > deploy/namespace.yaml
ssh-keygen -t ed25519 -q -N "" -C "flux-read-write" -f deploy/identity
ssh-keyscan github.com > deploy/known_hosts
cat <<-'EOF' > deploy/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
secretGenerator:
- files:
  - identity
  - identity.pub
  - known_hosts
  name: flux-system
  namespace: flux-system
generatorOptions:
  disableNameSuffixHash: true
EOF
# now apply that to the cluster:
kustomize build deploy | kubectl apply -f -
# Now add the contents of deploy/identity.pub as a GitHub deploy key here:
# https://github.com/PHACDataHub/cpho-phase2/settings/keys
```
