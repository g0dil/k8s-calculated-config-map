default: format test

all: package chart image

init:
	poetry install

test:
	poetry run flake8
	poetry run pytest

format:
	poetry run black .

package:
	poetry build --format wheel

chart:
	mkdir -p dist
	cd dist && helm package ../chart
.PHONY: chart

image:
	buildah bud --file Containerfile --tag calculatedconfigmap --volume "$(CURDIR):/work"

run:
	poetry run kopf run --module calculated_config_map
