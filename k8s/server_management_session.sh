#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

PROJECT_ID=pht-01hp04dtnkf
REGION=northamerica-northeast1
CLUSTER=hopic-cluster
SERVER_CONTAINER_NAME=server
SERVER_CONTAINER_REGISTRY=hopic-k8s-images
SERVER_CONTAINER_IMAGE_NAME=cpho-phase2
DEBUG_CONTAINER_IMAGE_NAME=cpho-phase2 #TODO, debug containers not part of CI/CD yet

server_image_name="${REGION}-docker.pkg.dev/${PROJECT_ID}/${SERVER_CONTAINER_REGISTRY}/${SERVER_CONTAINER_IMAGE_NAME}"
debug_image_name="${REGION}-docker.pkg.dev/${PROJECT_ID}/${SERVER_CONTAINER_REGISTRY}/${SERVER_CONTAINER_IMAGE_NAME}"

echo "Log in as your DMIA GCP user"
#gcloud auth login 

echo ""
echo "Getting cluster credentials..."
gcloud container clusters get-credentials "${CLUSTER}" --region "${REGION}" --project "${PROJECT_ID}"

echo ""
echo "Getting available server containers (looking for \`${server_image_name}:*\`)..."
# Gets a new-line delimited list of server containers on the cluster
# Each container line is a space delimited list of pod name, pod namespace, container name (the k8s name within the pod), and container image tag
# The `uniq -f 1` filters to one option per namespace (`-f 1`, a little confusingly, means ignore the first field, the pod name, while uniq-ing)
server_container_options=$(\
  kubectl get pods --all-namespaces -o \
  jsonpath='{range .items[*]}{"\n"}{.metadata.name}{" "}{.metadata.namespace}{" "}{range .spec.containers[*]}{"("}{.name}{","}{.image}{")"}{","}{end}{end}' \
  | grep -E "${server_image_name}" \
  | sed -E -e "s|^(.*)[ ](.*)[ ].*\(([^,]+),${server_image_name}:([^\),]+)\),.*$|\1 \2 \3 \4|g" \
  | sort \
  | uniq -f 1 \
)

server_container_option_count=$(echo "${server_container_options}" | wc -l)

if [[ ! "${server_container_option_count}" -gt "0" ]]; then
  echo ""
  echo "No server containers found in the cluster?! Has the image changed?"
  exit 1
fi

echo ""
echo "Possible target containers:"
echo -e "\tOption\tNamespace\tImage Tag"
for (( i=1; i<="${server_container_option_count}"; i++ )); do
  option=$(echo "${server_container_options}" | sed -n "${i}p")
  IFS=" " read -r pod_name namespace container_name image_tag <<< "${option}"

	echo -e "\t${i}\t${namespace}\t${image_tag}"
done
exit 1
read -p "Select from range 1-${server_container_option_count}: " selected_target

if [[ ! "${selected_target}" =~ ^[1-9]+$ ]]; then
  echo ""
  echo "Invalid selection \"${selected_target}\", must be a number in range 1-${server_container_option_count}"
  exit 1
fi
if ((! ($selected_target > 0 && $selected_target <= $server_container_option_count) )); then
  echo ""
  echo "Invalid selection \"${selected_target}\", must be in range 1-${server_container_option_count}"
  exit 1
fi

selected_option=$(echo "${server_container_options}" | sed -n "${selected_target}p")
IFS=" " read -r selected_pod_name selected_namespace selected_container_name selected_image_tag <<< "${selected_option}"

echo ""
echo "Attaching debug container image to selected server container, with shared process pool and cloned env vars..."
echo -e "\tTargetting \"${selected_container_name}\" container with tag \"${selected_image_tag}\" in namespace \"${selected_namespace}\" (pod \"${selected_pod_name}\")"
echo -e "\tAttaching debug container using ${debug_image_name}:${selected_image_tag}"

echo ""
echo "Tip: while the maintenance container is still alive (this terminal is attached), you can copy to/from the maintenance pod from your local machine using the following commands:"
echo -e "\tkubectl cp <local file path> ${selected_namespace}/${selected_pod_name}:<remote file path> -c <debug container name>"
echo -e "\tkubectl cp ${selected_namespace}/${selected_pod_name}:<remote file path> <local file path> -c <debug container name>"
echo "Where \"<debug container name>\" is the container name output below (looks like \"debugger-[a-z0-9]{5}\")"

echo ""
kubectl debug -it --namespace "${selected_namespace}" --target "${selected_container_name}" \
  --image "${debug_image_name}:${selected_image_tag}" "${selected_pod_name}"  \
  -- sh -c "export \$(strings /proc/1/environ) && sh"
# RE: the command passed to the debug container above
#   The debug container shares a process pool with the --target container (one of our live servers). In this shared pool,
#   the process with pid 1 (aka /proc/1) will be the container command of the server container (most likely gunicorn),
#   which will have the full set of prod env vars in its environ (including mounted secrets, in plain text, such as DB password).
#   The management session needs to copy the prod server env vars in to its own environ so it can, e.g., connect to and manage the
#   prod DB.
#   /proc/1/environ is a null-delimited file, but the `strings` command parses it out properly. Passing its output to `export` will
#   write all of the /proc/1 env vars to the management container environment.
#   To execute this in the correct order, resulting in an open shell with the correct env vars, I had to pass the container command to
#   `kubectl debug ...` as a command string (`sh -c`) ending in `&& sh`, to open an interactive shell after after the env var set up.   
