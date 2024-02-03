VERSION = 0.0.1

all: build

build: build-stamp

build-stamp: Dockerfile mock-smtp-3.py Makefile requirements.txt
	docker build -t mplattu/mock-smtp-3:$(VERSION) .
	docker tag mplattu/mock-smtp-3:$(VERSION) mplattu/mock-smtp-3:latest
	: > $@

push: build push-stamp

push-stamp: build-stamp
	docker push mplattu/mock-smtp-3:$(VERSION)
	docker push mplattu/mock-smtp-3:latest
	: > $@

clean:
	rm -f *~ *-stamp

requirements.txt:
	pip freeze >requirements.txt

.PHONY: all build push clean

