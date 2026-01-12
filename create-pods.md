# Pods Creation using Podman
## PostgreSQL
```bash
# create a network
podman network create aluna-net && \
podman volume create aluna-db-data && \
podman volume create aluna-db-config
# create the pod for PostgreSQL
podman pod create --name aluna-db-pod --network aluna-net --publish 5434:5432 && \
# run the PostgreSQL container in the pod
podman run --pod aluna-db-pod \
  --name aluna-db \
  -e POSTGRES_DB=chris_db \
  -e POSTGRES_USER=chris \
  -e POSTGRES_PASSWORD=maGazine1! \
  -v aluna-db-data:/var/lib/postgresql/data \
  -v aluna-db-config:/etc/postgresql/conf.d \
  --restart=always \
  -d docker.io/library/postgres:16.10-trixie


