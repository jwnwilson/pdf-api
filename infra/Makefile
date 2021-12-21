ENVIRONMENT:=staging
docker_tag:=latest

init:
	cd tf && terraform init -var-file="../${ENVIRONMENT}.tfvars"
	cd tf_pipeline && terraform init -var-file="../${ENVIRONMENT}.tfvars"

plan:
	cd tf && terraform plan -var-file="../${ENVIRONMENT}.tfvars"

apply:
	cd tf && TF_VAR_docker_tag=${docker_tag} terraform apply -var-file="../${ENVIRONMENT}.tfvars"

apply_pipeline:
	cd tf_pipeline && terraform apply -var-file="../${ENVIRONMENT}.tfvars"

destroy:
	cd tf && terraform destroy -var-file="../${ENVIRONMENT}.tfvars"
