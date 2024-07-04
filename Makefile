# Docker command to use, can be podman
ifneq (, $(shell which podman))
CONTAINER_RUNTIME := podman
else
ifneq (, $(shell which docker))
CONTAINER_RUNTIME := docker
else
$(error "Neither docker nor podman are available in PATH")
endif
endif

IMG_TAG ?= latest
IMG ?= quay.io/yblum/slack_server_mock:${IMG_TAG}

.PHONY: image-build
image-build: ## Build the container image.
	$(CONTAINER_RUNTIME) build -t ${IMG} .

.PHONY: image-push
image-push: ## Push the container image.
	$(CONTAINER_RUNTIME) push ${IMG}
