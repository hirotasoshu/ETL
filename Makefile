install:
	poetry install && cp config/.env.template config/.env && poetry run pre-commit install

up:
	docker-compose up --build -d

down:
	docker-compose down --remove-orphans

destroy:
	docker-compose down -v

etl-logs:
	docker-compose logs -f etl
