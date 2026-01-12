#!/bin/bash
# script to build image and send the kubernetes manifest yaml file to the server
set -euo pipefail

# VARIABLES
GIT_SHA=$(git rev-parse --short=8 HEAD)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD | sed 's/\//-/g')
IMAGE_NAME="docker.io/christianbueno1/aluna-api"
CONTAINERFILE="Containerfile"
PAT_FILE="$HOME/Documents/docker-pat.txt"
DOCKER_USER="christianbueno1"
REGISTRY="registry-1.docker.io"
MANIFEST_FILE=aluna-api-pod.yaml
SSH_ALIAS=az-odin
REMOTE_PATH=~/deployments/aluna-api/
PODMAN_NETWORK_NAME=aluna-net
PODNAME=aluna-api-pod

echo "📦 Building image with tags: ${IMAGE_NAME}:${GIT_BRANCH}, ${IMAGE_NAME}:${GIT_SHA}"
podman build -t ${IMAGE_NAME}:${GIT_BRANCH} -t ${IMAGE_NAME}:${GIT_SHA} -f ${CONTAINERFILE} .
echo "✅ Image built successfully."

# Authenticate to Docker Hub
echo "🔐 Authenticating to Docker Hub..."
podman login -u "$DOCKER_USER" --password-stdin "$REGISTRY" < "$PAT_FILE"
echo "✅ Authenticated successfully."

# push images
echo "🚀 Pushing images to Docker Hub..."
podman push ${IMAGE_NAME}:${GIT_BRANCH}
podman push ${IMAGE_NAME}:${GIT_SHA}
# if is main branch, also push latest tag
if [ "$GIT_BRANCH" == "main" ]; then
  podman tag ${IMAGE_NAME}:${GIT_SHA} ${IMAGE_NAME}:latest
  podman push ${IMAGE_NAME}:latest
fi
echo "✅ Images pushed successfully."

# Transfer manifest file to remote server, show progress, use rsync
echo "📡 Transferring manifest file to remote server..."
rsync -avz --mkpath --progress $MANIFEST_FILE $SSH_ALIAS:$REMOTE_PATH
echo "✅ Manifest file transferred successfully."

# Stop and remove existing pod on remote server, then create new pod
echo "🔄 Restarting pod on remote server..."
ssh $SSH_ALIAS "podman pod stop $PODNAME || true && podman pod rm $PODNAME || true && podman kube play --network $PODMAN_NETWORK_NAME $REMOTE_PATH$MANIFEST_FILE"
echo "✅ Pod restarted successfully."