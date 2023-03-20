# Flux

This folder contains the config needed to deploy the system with flux.
The config here was generated with the following commands:

```bash
# generate flux crds with only the features we use
flux install --export --components=source-controller,kustomize-controller,notification-controller > flux/crds.yaml
# Tell flux what repo and branch to watch
flux create source git github-repo --export --branch main --url "ssh://github.com/PHACDataHub/cpho-phase2.git" > flux/github-repo.yam
# tell flux to `kustomize build | kubectl apply` the ingress folder for that repo
flux create kustomization ingress --export --path istio --source github-repo > flux/ingress-kustomization.yaml
# tell flux to `kustomize build | kubectl apply` the frontend folder after istio starts
# Istio needs to be running for it to inject sidecar containers
flux create kustomization frontend --export --path frontend --source github-repo --health-check=Deployment/istio-ingressgateway.istio-ingress > flux/frontend-kustomization.yaml
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
