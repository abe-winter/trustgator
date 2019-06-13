DBNAME = trustgator-db
REDISNAME = tgtr-redis
USER = postgres
docker-dev:
	# docker for local development
	docker run -d --name $(DBNAME) postgres || echo db init failed
	docker run -d --name $(REDISNAME) redis || echo redis init failed

db-host:
	@docker inspect -f '{{.NetworkSettings.IPAddress}}' $(DBNAME)

redis-host:
	@docker inspect -f '{{.NetworkSettings.IPAddress}}' $(REDISNAME)

migrate-dev:
	$(eval HOST := $(shell make db-host))
	ls sql/migrate/*.sql | xargs -n 1 psql --host $(HOST) --user $(USER) -f

psql:
	$(eval HOST := $(shell make db-host))
	psql --host $(HOST) --user $(USER)

redis-cli:
	$(eval HOST := $(shell make redis-host))
	redis-cli -h $(HOST)

serve:
	# optionally run this with `FLASK_DEBUG=1 make serve` to get debugger and reloading
	FLASK_APP=trustgator.main flask run
