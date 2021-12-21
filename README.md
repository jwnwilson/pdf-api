# FastAPI template

A serverless (AWS lambda) FastAPI template intended to be extended with other microservices using SQS to communicate between services.

# Requirements

This project requires installed on your OS.

- docker and docker-compose
- makefile command
- terraform (version 1.1.1)

# Running locally

To start the project run the command:

`make run`

This will build a lambda friendly the docker container running fast api that can be accessed via:

`http://localhost:8888`

# Deploying to AWS

To deploy this project copy infra/tf/template.tfvars -> infra/tf/staging.tfvars and add:

aws_access_key = "replace me"
aws_secret_key = "replace me"

This can also be done via terraform ENV Vars if desired:

export TF_VAR_aws_access_key=""
export TF_VAR_aws_secret_key=""

Then inside infra/ folder run:

`make init`
`make plan`
`make apply`

This will prepare and build a staging environment for this project, to destroy the environment run:

`make destroy`

To create a different environment run:

`ENVIRONMENT=test make init`
`ENVIRONMENT=test make plan`
`ENVIRONMENT=test make apply`

# Domain Driven Development

The structure of this project is based on a DDD programming technique "Hexagonal architecture" as described here:
https://medium.com/ssense-tech/hexagonal-architecture-there-are-always-two-sides-to-every-story-bc0780ed7d9c

The goal is to avoid coupling logic so that it can be re-used across projects.