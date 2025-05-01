all: help

# Set default values for the build arguments
NEXT_PUBLIC_API_URL ?= http://example.com/api
NEXT_PUBLIC_API_URL_CREATE_PASSWORD ?= http://example.com/create-password
NEXT_PUBLIC_FIREBASE_API_KEY ?= your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN ?= your-firebase-auth-domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID ?= your-firebase-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET ?= your-firebase-storage-bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID ?= your-firebase-messaging-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID ?= your-firebase-app-id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID ?= your-firebase-measurement-id
NEXT_PUBLIC_API ?= http://example.com/api
NEXT_PUBLIC_MANAGE_PASSWORD_UI ?= http://example.com/manage-password-ui
IMAGE_NAME ?= persimmon-app
TAG ?= latest

# Generate commands to set environment
setenv:
	@echo "generate the export commands for the next public environment variables"
	grep -v "^[ ]*#" .env* | grep NEXT_PUBLIC_ | sed -e "s/^/export /" -e "s/[ ]*=[ ]*/=/"
	@echo "copy paste the above lines in the shell to set the environment"

# Generate commands to unset environment
unsetenv:
	@echo "generate the commands for unexporting the next public environment variables"
	# grep -v "^[ ]*#" .env* | grep NEXT_PUBLIC_ | sed -e "s/^/unset /" -e "s/[ ]*=.*//"
	env | grep NEXT_PUBLIC_ | sed -e "s/^/unset /" -e "s/[ ]*=.*//"
	@echo "copy paste the above lines in the shell to unset the environment"

# Docker build command
build:
	@echo "Building Docker image..."
	docker build \
		--build-arg NEXT_PUBLIC_API_URL=$(NEXT_PUBLIC_API_URL) \
		--build-arg NEXT_PUBLIC_API_URL_CREATE_PASSWORD=$(NEXT_PUBLIC_API_URL_CREATE_PASSWORD) \
		--build-arg NEXT_PUBLIC_FIREBASE_API_KEY=$(NEXT_PUBLIC_FIREBASE_API_KEY) \
		--build-arg NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=$(NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN) \
		--build-arg NEXT_PUBLIC_FIREBASE_PROJECT_ID=$(NEXT_PUBLIC_FIREBASE_PROJECT_ID) \
		--build-arg NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=$(NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET) \
		--build-arg NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=$(NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID) \
		--build-arg NEXT_PUBLIC_FIREBASE_APP_ID=$(NEXT_PUBLIC_FIREBASE_APP_ID) \
		--build-arg NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=$(NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID) \
		--build-arg NEXT_PUBLIC_API=$(NEXT_PUBLIC_API) \
		--build-arg NEXT_PUBLIC_MANAGE_PASSWORD_UI=$(NEXT_PUBLIC_MANAGE_PASSWORD_UI) \
		-t $(IMAGE_NAME):$(TAG) .

# Docker run command
run:
	@echo "Running Docker container..."
	docker run -p 3000:3000 --rm $(IMAGE_NAME):$(TAG)

# Docker image cleanup command
clean:
	@echo "Cleaning up Docker images..."
	docker rmi $(IMAGE_NAME):$(TAG)

# Help command (to display available Makefile targets)
help:
	@echo "Makefile for Docker"
	@echo ""
	@echo "Available targets:"
	@echo "  setenv     - generate commands to set the environment"
	@echo "  unsetenv   - generate commands to unset the environment"
	@echo "  build      - Build the Docker image"
	@echo "  run        - Run the Docker container"
	@echo "  clean      - Remove the Docker image"
	@echo "  help       - Display this help message"

