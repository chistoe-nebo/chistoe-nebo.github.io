IMAGE=nebo:latest
DOCKER_OPTS=-v ${PWD}:/app

build: docker
	docker run --rm $(DOCKER_OPTS) $(IMAGE) make -C /app -f Makefile.site build

docker:
	docker build -t $(IMAGE) -f build/Dockerfile .

serve:
	docker run --rm $(DOCKER_OPTS) -p 8081:8080 $(IMAGE) make -C /app -f Makefile.site serve

shell:
	docker run -it --rm $(DOCKER_OPTS) $(IMAGE) sh -l

.PHONY: build
