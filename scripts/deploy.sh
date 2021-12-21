#! /bin/bash

set -e
set -x

region="eu-west-1"
aws_ecr="675468650888.dkr.ecr.eu-west-1.amazonaws.com"
ecr_repo_name="pdf_service_api"
latest_image=`docker images -q fastapi-template-api`
docker_tag=$(date '+%d%m%Y%H%M%S')

# Docker login
source ./scripts/docker.sh

# tag and push docker image
docker tag "${latest_image}" "${aws_ecr}/${ecr_repo_name}:latest"
docker tag "${latest_image}" "${aws_ecr}/${ecr_repo_name}:${docker_tag}"
docker push "${aws_ecr}/${ecr_repo_name}:latest"
docker push "${aws_ecr}/${ecr_repo_name}:${docker_tag}"

# Deploy image to lambda
cd infra
docker_tag=${docker_tag} make apply
