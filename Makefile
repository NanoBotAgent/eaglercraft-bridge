.PHONY: setup start stop test test-all docker-build docker-run clean

setup:
	@bash scripts/download_all.sh

start:
	@bash scripts/start_all.sh

stop:
	@bash scripts/stop_all.sh

test:
	@pip install -r requirements.txt -q
	@pytest tests/ -v

test-all: setup start
	@sleep 5
	@$(MAKE) test
	@$(MAKE) stop

docker-build:
	@cd docker && docker compose build

docker-run: docker-build
	@cd docker && docker compose up

clean:
	@rm -f proxy/BungeeCord.jar proxy/plugins/*.jar
	@rm -f backend/paper-26.1.2.jar backend/plugins/*.jar
	@rm -rf backend/world backend/cache backend/logs
	@rm -rf proxy/logs
