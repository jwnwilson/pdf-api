#! /bin/bash

set -e
set -

# Use last commit datetime as git tag
docker_tag=$(git log -n1 --pretty='format:%cd' --date=format:'%Y%m%d%H%M%S')

# Deploy image to lambda
cd infra
docker_tag=${docker_tag} make apply