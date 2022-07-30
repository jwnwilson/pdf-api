DOCKER_NAME=api
DOCKER_COMMAND=docker-compose -f docker-compose.yml
LOCAL_TASK_URL=http://localhost:9000/2015-03-31/functions/function/invocations

build:
	bash ./scripts/build.sh

# push last build image to ECR
push:
	bash ./scripts/push.sh

run:
	${DOCKER_COMMAND} up

stop:
	${DOCKER_COMMAND} down

test:
	${DOCKER_COMMAND} run ${DOCKER_NAME} bash -c "pytest app"

lint:
	${DOCKER_COMMAND} run ${DOCKER_NAME} bash -c "scripts/lint.sh"

static:
	${DOCKER_COMMAND} run ${DOCKER_NAME} bash -c "scripts/lint.sh --check"

# Requires "make init_pipeline apply_pipeline" to be run in infra/ first
deploy:
	bash ./scripts/deploy.sh

clean:
	rm **/**/*.pyc
	rm **/**/__pycache__
