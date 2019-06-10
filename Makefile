DBNAME = trustgator-db
USER = postgres
docker-dev:
	# docker for local development
	docker run -d --name $(DBNAME) postgres

db-host:
	@docker inspect -f '{{.NetworkSettings.IPAddress}}' $(DBNAME)

migrate-dev:
	$(eval HOST := $(shell make db-host))
	ls sql/migrate/*.sql | xargs psql --host $(HOST) --user $(USER) -f

psql:
	$(eval HOST := $(shell make db-host))
	psql --host $(HOST) --user $(USER)

serve:
	# optionally run this with `FLASK_DEBUG=1 make serve` to get debugger and reloading
	FLASK_APP=trustgator.main flask run
