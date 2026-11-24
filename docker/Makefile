.PHONY: test run docker docker-qpu docker-quanso smoke down

test:
	python3 -m pytest -q tests

run:
	python3 -m zephirum_core.server

docker:
	docker compose up -d --build core

docker-qpu:
	docker compose --profile qpu up -d --build core-qpu

docker-quanso:
	docker compose --profile quanso run --rm quanso-tests

smoke:
	curl -s localhost:8080/health | head -20

down:
	docker compose --profile qpu --profile quanso down
